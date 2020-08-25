from grammar import SoLangVisitor, SoLangParser
import llvmlite.ir as ir
import llvmlite.binding as llvm


class MyVisitor(SoLangVisitor):
    def visitCompilationUnit(self, ctx: SoLangParser.CompilationUnitContext):
        # function table
        self.functions = {}

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
        self.fn_write = ir.Function(self.module, ftype_write, name="write")

        self.visitChildren(ctx)

        # generate code
        llvm_ir = str(self.module)
        llvm_ir_parsed = llvm.parse_assembly(llvm_ir)

        # optimizer
        pmb = llvm.create_pass_manager_builder()
        pmb.opt_level = 1
        pm = llvm.create_module_pass_manager()
        pmb.populate(pm)
        pm.run(llvm_ir_parsed)

        with open("build/out.ll", "w") as f:
            f.write(str(llvm_ir_parsed))

        return None

    def visitFunction(self, ctx: SoLangParser.FunctionContext):
        name = ctx.Ident().getText()
        block_name = name

        # register function
        ftype = ir.FunctionType(self.i64, [])
        self.functions[name] = ir.Function(self.module, ftype, name=name)
        block = self.functions[name].append_basic_block(name=block_name)

        # make a block for func
        self.builder = ir.IRBuilder(block)

        ret = self.visitChildren(ctx)

        # ret is always None
        return ret

    def visitWriteStmt(self, ctx: SoLangParser.WriteStmtContext):
        # call write()
        arg = self.visit(ctx.expr())
        ret = self.builder.call(self.fn_write, (arg,), name="write")
        return ret

    def visitReturnStmt(self, ctx: SoLangParser.ReturnStmtContext):
        ret = self.visit(ctx.expr())
        return self.builder.ret(ret)
        # float to unsigned int
        # ret = self.builder.fptoui(ret, self.i64, name="r")
        # return self.builder.ret(ret)

    def visitParExpr(self, ctx: SoLangParser.ParExprContext):
        return self.visit(ctx.children[1])

    def visitUnaryExpr(self, ctx: SoLangParser.UnaryExprContext):
        ret = self.visit(ctx.children[1])
        if ctx.children[0].getText() == '-':
            ret = self.builder.mul(
                ret, ir.Constant(
                    self.i64, -1), name='mul_tmp')
        return ret

    def visitMulDivExpr(self, ctx: SoLangParser.MulDivExprContext):
        lhs = self.visit(ctx.children[0])
        rhs = self.visit(ctx.children[2])
        if ctx.children[1].getText() == '*':
            ret = self.builder.mul(lhs, rhs, name='mul_tmp')
        else:
            ret = self.builder.sdiv(lhs, rhs, name='div_tmp')
        return ret

    def visitAddSubExpr(self, ctx: SoLangParser.AddSubExprContext):
        lhs = self.visit(ctx.children[0])
        rhs = self.visit(ctx.children[2])
        if ctx.children[1].getText() == '+':
            ret = self.builder.add(lhs, rhs, name='add_tmp')
        else:
            ret = self.builder.sub(lhs, rhs, name='sub_tmp')
        return ret

    def visitNumberExpr(self, ctx: SoLangParser.NumberExprContext):
        return ir.Constant(self.i64, int(ctx.Number().getText()))

    def visitFunctionCallExpr(self, ctx: SoLangParser.FunctionCallExprContext):
        # call function
        fn_name = ctx.Ident().getText()
        ret = self.builder.call(self.functions[fn_name], (), name="fn_name")
        return ret
