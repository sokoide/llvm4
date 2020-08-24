from grammar import SoLangVisitor, SoLangParser
import llvmlite.ir as ir
import llvmlite.binding as llvm


class MyVisitor(SoLangVisitor):
    def visitProg(self, ctx: SoLangParser.ProgContext):
        # llvm init
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        # define types
        self.i64 = ir.IntType(64)
        self.f64 = ir.FloatType()

        # int64_t main()
        ftype_main = ir.FunctionType(self.i64, [])
        module = ir.Module(name='sokoide_module')
        fn_main = ir.Function(module, ftype_main, name="main")
        block = fn_main.append_basic_block(name='entrypoint')

        # function prototype (external linkage implemented in builtin.c) for
        # void write(int64_t)
        ftype_write = ir.FunctionType(ir.VoidType(), [self.f64])
        self.fn_write = ir.Function(module, ftype_write, name="write")

        # make a block for main (entrypoint)
        self.builder = ir.IRBuilder(block)

        # visit children
        ret = self.visitChildren(ctx)

        # return 0
        self.builder.ret(ir.Constant(self.i64, 0))

        llvm_ir = str(module)
        llvm_ir_parsed = llvm.parse_assembly(llvm_ir)

        # optimizer
        pmb = llvm.create_pass_manager_builder()
        pmb.opt_level = 1
        pm = llvm.create_module_pass_manager()
        pmb.populate(pm)
        pm.run(llvm_ir_parsed)

        with open("build/out.ll", "w") as f:
            f.write(str(llvm_ir_parsed))

        # ret is always None
        return ret

    def visitWriteStmt(self, ctx: SoLangParser.WriteStmtContext):
        # call write()
        arg = self.visit(ctx.expr())
        ret = self.builder.call(self.fn_write, (arg,), name="write")
        return ret

    def visitParExpr(self, ctx: SoLangParser.ParExprContext):
        return self.visit(ctx.children[1])

    def visitUnaryExpr(self, ctx: SoLangParser.UnaryExprContext):
        ret = self.visit(ctx.children[1])
        if ctx.children[0].getText() == '-':
            ret = self.builder.fmul(
                ret, ir.Constant(
                    self.f64, -1), name='mul_tmp')
        return ret

    def visitMulDivExpr(self, ctx: SoLangParser.MulDivExprContext):
        lhs = self.visit(ctx.children[0])
        rhs = self.visit(ctx.children[2])
        if ctx.children[1].getText() == '*':
            ret = self.builder.fmul(lhs, rhs, name='mul_tmp')
        else:
            ret = self.builder.fdiv(lhs, rhs, name='div_tmp')
        return ret

    def visitAddSubExpr(self, ctx: SoLangParser.AddSubExprContext):
        lhs = self.visit(ctx.children[0])
        rhs = self.visit(ctx.children[2])
        if ctx.children[1].getText() == '+':
            ret = self.builder.fadd(lhs, rhs, name='add_tmp')
        else:
            ret = self.builder.fsub(lhs, rhs, name='sub_tmp')
        return ret

    def visitNumberExpr(self, ctx: SoLangParser.NumberExprContext):
        return ir.Constant(self.f64, float(ctx.NUMBER().getText()))
