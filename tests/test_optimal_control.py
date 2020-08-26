"""
Created on 25/08/2020, 15.55

@author: blauths
"""

import pytest
from fenics import *
import cashocs
import numpy as np



config = cashocs.create_config('./config_ocp.ini')

mesh, subdomains, boundaries, dx, ds, dS = cashocs.regular_mesh(10)
V = FunctionSpace(mesh, 'CG', 1)

y = Function(V)
p = Function(V)
u = Function(V)

F = inner(grad(y), grad(p))*dx - u*p*dx
bcs = cashocs.create_bcs_list(V, Constant(0), boundaries, [1, 2, 3, 4])

y_d = Expression('sin(2*pi*x[0])*sin(2*pi*x[1])', degree=1, domain=mesh)
alpha = 1e-6
J = Constant(0.5)*(y - y_d)*(y - y_d)*dx + Constant(0.5*alpha)*u*u*dx

ocp = cashocs.OptimalControlProblem(F, bcs, J, y, u, p, config)

cc = [0, 100]

ocp_cc = cashocs.OptimalControlProblem(F, bcs, J, y, u, p, config, control_constraints=cc)



def test_control_gradient():
	assert cashocs.verification.control_gradient_test(ocp) > 1.9
	assert cashocs.verification.control_gradient_test(ocp) > 1.9
	assert cashocs.verification.control_gradient_test(ocp) > 1.9



def test_control_gd():
	u.vector()[:] = 0.0
	ocp.solve('gd', rtol=1e-2, atol=0.0, max_iter=50)
	assert ocp.solver.relative_norm <= ocp.solver.rtol



def test_control_cg():
	u.vector()[:] = 0.0
	ocp.solve('cg', rtol=1e-2, atol=0.0, max_iter=30)
	assert ocp.solver.relative_norm <= ocp.solver.rtol



def test_control_bfgs():
	u.vector()[:] = 0.0
	ocp.solve('bfgs', rtol=1e-2, atol=0.0, max_iter=10)
	assert ocp.solver.relative_norm <= ocp.solver.rtol



def test_control_newton():
	u.vector()[:] = 0.0
	ocp.solve('newton', rtol=1e-2, atol=0.0, max_iter=2)
	assert ocp.solver.relative_norm <= ocp.solver.rtol



def test_control_gd_cc():
	u.vector()[:] = 0.0
	ocp_cc.solve('gd', rtol=1e-2, atol=0.0, max_iter=25)
	assert ocp_cc.solver.relative_norm <= ocp_cc.solver.rtol
	assert np.alltrue(ocp_cc.controls[0].vector()[:] >= cc[0])
	assert np.alltrue(ocp_cc.controls[0].vector()[:] <= cc[1])



def test_control_cg_cc():
	u.vector()[:] = 0.0
	ocp_cc.solve('cg', rtol=1e-2, atol=0.0, max_iter=25)
	assert ocp_cc.solver.relative_norm <= ocp_cc.solver.rtol
	assert np.alltrue(ocp_cc.controls[0].vector()[:] >= cc[0])
	assert np.alltrue(ocp_cc.controls[0].vector()[:] <= cc[1])



def test_control_lbfgs_cc():
	u.vector()[:] = 0.0
	ocp_cc.solve('lbfgs', rtol=1e-2, atol=0.0, max_iter=12)
	assert ocp_cc.solver.relative_norm <= ocp_cc.solver.rtol
	assert np.alltrue(ocp_cc.controls[0].vector()[:] >= cc[0])
	assert np.alltrue(ocp_cc.controls[0].vector()[:] <= cc[1])



# ocp.solve('newton', rtol=1e-2, atol=0.0, max_iter=2)
