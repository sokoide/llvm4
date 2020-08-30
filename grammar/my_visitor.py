from grammar import SoLangVisitor, SoLangParser
import llvmlite.ir as ir
import llvmlite.binding as llvm
import argparse


class MyVisitor(SoLangVisitor):
    def __init__(self, args: argparse.Namespace):
        self.optimize = args.optimize

    def visitCompilationUnit(self, ctx: SoLangParser.CompilationUnitContext):
        # global function table
        # functions[function-name] = function-pointer
        self.functions = {}
        # global variable table
        # variables[function-name][variable-name] = variable-pointer
        self.variables = {}
        self.current_function = ''

        # llvm init
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        # define types
        self.i64 = ir.IntType(64)
        self.f64 = ir.FloatType()

        self.module = ir.Module(name='sokoide_module')
        # function prototype (external linkage implemented in builtin.c) for
        # void write(int64_t)
        ftype_write = ir.FunctionType(ir.VoidType(), [self.i64])
        self.fn_write = ir.Function(self.module, ftype_write, name='write')

        self.visitChildren(ctx)

        # generate code
        llvm_ir = str(self.module)
        llvm_ir_parsed = llvm.parse_assembly(llvm_ir)

        # optimizer
        if self.optimize:
            pmb = llvm.create_pass_manager_builder()
            pmb.opt_level = 1
            pm = llvm.create_module_pass_manager()
            pmb.populate(pm)
            pm.run(llvm_ir_parsed)

        with open('build/out.ll', 'w') as f:
            f.write(str(llvm_ir_parsed))

        return None

    def visitFunction(self, ctx: SoLangParser.FunctionContext):
        name = ctx.Ident().getText()
        block_name = 'entry'
        self.current_function = name
        self.variables[self.current_function] = {}

        params = []
        paramnames = []
        if ctx.paramdefs() is not None:
            for paramdef in self.visit(ctx.paramdefs()):
                params.append(self.i64)
                paramnames.append(paramdef)

        # register function
        ftype = ir.FunctionType(self.i64, params)
        func = ir.Function(self.module, ftype, name=name)
        entrybb = func.append_basic_block(name=block_name)
        retbb = ir.Block(entrybb, name='_ret')
        # retbb = func.append_basic_block(name='ret')
        self.functions[name] = {
                'func': func,
                'entrybb': entrybb,
                'retbb': retbb
                }

        # make a block for func entry
        self.builder = ir.IRBuilder(entrybb)

        # define variables for the paramnames
        for paramname in paramnames:
            var = self.builder.alloca(self.i64, size=8, name=paramname)
            self.variables[self.current_function][paramname] = var

        # create _ret variable
        var = self.builder.alloca(self.i64, size=8, name='_ret')
        self.variables[self.current_function]['_ret'] = var

        # store parameter values to the variables
        i = 0
        for paramname in paramnames:
            ptr = self.variables[self.current_function][paramname]
            value = func.args[i]
            self.builder.store(value, ptr)
            i += 1

        ret = self.visitChildren(ctx)

        # make a block for ret
        func.basic_blocks.append(retbb)
        self.builder = ir.IRBuilder(retbb)
        ptr = self.variables[self.current_function]['_ret']
        value = self.builder.load(ptr, name)
        self.builder.ret(value)

        # ret is always None
        return ret

    def visitVariableDefinitionStmt(
            self, ctx: SoLangParser.VariableDefinitionStmtContext):
        name = ctx.Ident().getText()
        # create variable
        var = self.builder.alloca(self.i64, size=8, name=name)
        self.variables[self.current_function][name] = var
        return None

    def visitAsgnStmt(self, ctx: SoLangParser.AsgnStmtContext):
        name = ctx.Ident().getText()
        value = self.visit(ctx.expr())
        ptr = self.variables[self.current_function][name]
        self.builder.store(value, ptr)
        return None

    def visitWriteStmt(self, ctx: SoLangParser.WriteStmtContext):
        # call write()
        args = (self.visit(ctx.expr()),)
        ret = self.builder.call(self.fn_write, (args), name='write')
        return ret

    def visitReturnStmt(self, ctx: SoLangParser.ReturnStmtContext):
        value = self.visit(ctx.expr())
        ptr = self.variables[self.current_function]['_ret']
        self.builder.store(value, ptr)
        self.builder.branch(self.functions[self.current_function]['retbb'])
        return None

    def visitIf_stmt(self, ctx: SoLangParser.If_stmtContext):
        cond = self.visit(ctx.cond())
        with self.builder.if_else(cond) as (then, otherwise):
            with then:
                self.visit(ctx.block())
            with otherwise:
                if ctx.else_block() is not None:
                    self.visit(ctx.else_block())

    def visitElse_block(self, ctx: SoLangParser.Else_blockContext):
        return self.visitChildren(ctx)

    def visitElseif_block(self, ctx: SoLangParser.Elseif_blockContext):
        return self.visitChildren(ctx)

    def visitCond(self, ctx: SoLangParser.CondContext):
        if len(ctx.children) == 1:
            # expr
            return self.visit(ctx.children[0])
        else:
            # expr cond expr
            if ctx.children[1].getText() == '==':
                return self.builder.icmp_signed(
                    '==', self.visit(
                        ctx.expr(0)), self.visit(
                        ctx.expr(1)), 'eq')
            elif ctx.children[1].getText() == '!=':
                return self.builder.icmp_signed(
                    '!=', self.visit(
                        ctx.expr(0)), self.visit(
                        ctx.expr(1)), 'ne')
            elif ctx.children[1].getText() == '<=':
                return self.builder.icmp_signed(
                    '<=', self.visit(
                        ctx.expr(0)), self.visit(
                        ctx.expr(1)), 'le')
            elif ctx.children[1].getText() == '<':
                return self.builder.icmp_signed(
                    '<', self.visit(
                        ctx.expr(0)), self.visit(
                        ctx.expr(1)), 'lt')
            elif ctx.children[1].getText() == '>=':
                return self.builder.icmp_signed(
                    '>=', self.visit(
                        ctx.expr(0)), self.visit(
                        ctx.expr(1)), 'ge')
            elif ctx.children[1].getText() == '>':
                return self.builder.icmp_signed(
                    '>', self.visit(
                        ctx.expr(0)), self.visit(
                        ctx.expr(1)), 'gt')

    def visitUnaryExpr(self, ctx: SoLangParser.UnaryExprContext):
        ret = self.visit(ctx.children[1])
        if ctx.children[0].getText() == '-':
            ret = self.builder.mul(
                ret, ir.Constant(
                    self.i64, -1), name='mul_tmp')
        return ret

    def visitMulDivExpr(self, ctx: SoLangParser.MulDivExprContext):
        lhs = self.visit(ctx.expr(0))
        rhs = self.visit(ctx.expr(1))
        if ctx.children[1].getText() == '*':
            ret = self.builder.mul(lhs, rhs, name='mul_tmp')
        else:
            ret = self.builder.sdiv(lhs, rhs, name='div_tmp')
        return ret

    def visitAddSubExpr(self, ctx: SoLangParser.AddSubExprContext):
        lhs = self.visit(ctx.expr(0))
        rhs = self.visit(ctx.expr(1))
        if ctx.children[1].getText() == '+':
            ret = self.builder.add(lhs, rhs, name='add_tmp')
        else:
            ret = self.builder.sub(lhs, rhs, name='sub_tmp')
        return ret

    def visitParExpr(self, ctx: SoLangParser.ParExprContext):
        return self.visit(ctx.children[1])

    def visitNumberExpr(self, ctx: SoLangParser.NumberExprContext):
        return ir.Constant(self.i64, int(ctx.Number().getText()))

    def visitFunctionCallExpr(self, ctx: SoLangParser.FunctionCallExprContext):
        # call function
        fn_name = ctx.Ident().getText()
        args = self.visit(ctx.params())
        ret = self.builder.call(self.functions[fn_name]['func'], args, name=fn_name)
        return ret

    def visitIdentExpr(self, ctx: SoLangParser.IdentExprContext):
        name = ctx.Ident().getText()
        if name in self.variables[self.current_function]:
            ptr = self.variables[self.current_function][name]
            return self.builder.load(ptr, name)
        else:
            return None

    def visitParamdefs(self, ctx: SoLangParser.ParamdefsContext):
        ret = []
        for child in ctx.children:
            if isinstance(child, SoLangParser.ParamdefsContext):
                ret += self.visit(child)
            elif isinstance(child, SoLangParser.ParamdefContext):
                ret.append(self.visit(child))
        return ret

    def visitParamdef(self, ctx: SoLangParser.ParamdefContext):
        return ctx.Ident().getText()

    def visitParams(self, ctx: SoLangParser.ParamsContext):
        ret = []
        for child in ctx.children:
            if isinstance(child, SoLangParser.ParamsContext):
                ret += self.visit(child)
            elif isinstance(child, SoLangParser.ParamContext):
                ret.append(self.visit(child))
        return ret

    def visitParam(self, ctx: SoLangParser.ParamContext):
        return self.visit(ctx.children[0])
