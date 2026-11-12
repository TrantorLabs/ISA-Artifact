"""Use official Z3 via its installed C library, or a z3 executable.
No Python z3 package is necessary. No SAT/UNSAT result is fabricated.
"""
from __future__ import annotations
import ctypes
import ctypes.util
import shutil
import subprocess
import re

class Z3:
    def __init__(self):
        self.command=shutil.which('z3')
        name=ctypes.util.find_library('z3')
        self.lib=None
        if name:
            l=ctypes.CDLL(name); self.lib=l
            declarations={
                'Z3_mk_config':([],ctypes.c_void_p),
                'Z3_set_param_value':([ctypes.c_void_p,ctypes.c_char_p,ctypes.c_char_p],None),
                'Z3_del_config':([ctypes.c_void_p],None),
                'Z3_mk_context':([ctypes.c_void_p],ctypes.c_void_p),
                'Z3_del_context':([ctypes.c_void_p],None),
                'Z3_mk_solver':([ctypes.c_void_p],ctypes.c_void_p),
                'Z3_solver_inc_ref':([ctypes.c_void_p,ctypes.c_void_p],None),
                'Z3_solver_dec_ref':([ctypes.c_void_p,ctypes.c_void_p],None),
                'Z3_solver_from_string':([ctypes.c_void_p,ctypes.c_void_p,ctypes.c_char_p],None),
                'Z3_solver_check':([ctypes.c_void_p,ctypes.c_void_p],ctypes.c_int),
                'Z3_solver_get_model':([ctypes.c_void_p,ctypes.c_void_p],ctypes.c_void_p),
                'Z3_model_to_string':([ctypes.c_void_p,ctypes.c_void_p],ctypes.c_char_p),
                'Z3_get_full_version':([],ctypes.c_char_p),
                'Z3_solver_get_reason_unknown':([ctypes.c_void_p,ctypes.c_void_p],ctypes.c_char_p),
            }
            for n,(args,result) in declarations.items():
                f=getattr(l,n);f.argtypes=args;f.restype=result
            self.version=l.Z3_get_full_version().decode()
        elif self.command:
            self.version=subprocess.check_output([self.command,'-version'],text=True).strip()
        else:
            raise RuntimeError('Z3 executable or libz3 is required; formal results were NOT run')

    def solve(self,script: str):
        if self.lib is None:
            first=subprocess.run([self.command,'-in','-smt2'],input=script+'\n(check-sat)\n',text=True,capture_output=True,timeout=20)
            status=first.stdout.splitlines()[0].strip() if first.stdout else 'error'
            if first.returncode!=0 or status not in ('sat','unsat','unknown'):
                raise RuntimeError(first.stdout+first.stderr)
            model=''
            if status=='sat':
                more=subprocess.run([self.command,'-in','-smt2'],input=script+'\n(check-sat)\n(get-model)\n',text=True,capture_output=True,timeout=20,check=True)
                model=more.stdout
            return {'status':status.upper(),'model':model,'reason':''}
        l=self.lib;cfg=l.Z3_mk_config();l.Z3_set_param_value(cfg,b'timeout',b'10000')
        ctx=l.Z3_mk_context(cfg);l.Z3_del_config(cfg);solver=l.Z3_mk_solver(ctx);l.Z3_solver_inc_ref(ctx,solver)
        try:
            l.Z3_solver_from_string(ctx,solver,script.encode())
            status=l.Z3_solver_check(ctx,solver)
            result={'status':{1:'SAT',-1:'UNSAT',0:'UNKNOWN'}[status],'model':'','reason':''}
            if status==1:
                result['model']=l.Z3_model_to_string(ctx,l.Z3_solver_get_model(ctx,solver)).decode()
            elif status==0:
                result['reason']=l.Z3_solver_get_reason_unknown(ctx,solver).decode()
            return result
        finally:
            l.Z3_solver_dec_ref(ctx,solver);l.Z3_del_context(ctx)
