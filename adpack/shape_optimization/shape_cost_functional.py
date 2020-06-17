"""
Created on 24/02/2020, 08.44

@author: blauths
"""

import fenics



class ReducedCostFunctional:
	
	def __init__(self, shape_form_handler, state_problem):
		"""An implementation of the reduced cost functional
		
		Parameters
		----------
		shape_form_handler : adpack.forms.FormHandler or adpack.forms.ShapeFormHandler
			the FormHandler object for the optimization problem
		state_problem : adpack.pde_problems.state_problem.StateProblem
			the StateProblem object corresponding to the state system
		"""
		
		self.shape_form_handler = shape_form_handler
		self.state_problem = state_problem
		self.regularization = self.shape_form_handler.regularization



	def compute(self):
		"""Evaluates the reduced cost functional by first solving the state system and then evaluating the cost functional
		
		Returns
		-------
		 : float
			the value of the reduced cost functional at the current control

		"""
		
		self.state_problem.solve()
		# self.regularization.update_geometric_quantities()
		
		return fenics.assemble(self.shape_form_handler.cost_functional_form) + self.regularization.compute_objective()