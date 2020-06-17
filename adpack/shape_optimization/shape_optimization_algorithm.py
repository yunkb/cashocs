"""
Created on 15/06/2020, 08.00

@author: blauths
"""

import fenics
import json



class OptimizationAlgorithm:

	def __init__(self, optimization_problem):
		"""Parent class for the optimization methods implemented in adpack.optimization.methods

		Parameters
		----------
		optimization_problem : adpack.shape_optimization.shape_optimization_problem.ShapeOptimizationProblem
			the OptimalControlProblem class as defined through the user
		"""

		self.line_search_broken = False

		self.optimization_problem = optimization_problem
		self.shape_form_handler = self.optimization_problem.shape_form_handler
		self.state_problem = self.optimization_problem.state_problem
		self.config = self.state_problem.config
		self.adjoint_problem = self.optimization_problem.adjoint_problem

		self.shape_gradient_problem = self.optimization_problem.shape_gradient_problem
		self.gradient = self.shape_gradient_problem.gradient
		self.cost_functional = self.optimization_problem.reduced_cost_functional
		self.search_direction = fenics.Function(self.shape_form_handler.deformation_space)

		self.iteration = 0
		self.objective_value = 1.0
		self.gradient_norm_initial = 1.0
		self.relative_norm = 1.0
		self.stepsize = 1.0

		self.output_dict = dict()
		self.output_dict['cost_function_value'] = []
		self.output_dict['gradient_norm'] = []
		self.output_dict['stepsize'] = []
		self.output_dict['MeshQuality'] = []

		self.verbose = self.config.getboolean('OptimizationRoutine', 'verbose')
		self.save_results = self.config.getboolean('OptimizationRoutine', 'save_results')
		self.rtol = self.config.getfloat('OptimizationRoutine', 'rtol')
		self.atol = self.config.getfloat('OptimizationRoutine', 'atol')
		self.maximum_iterations = self.config.getint('OptimizationRoutine', 'maximum_iterations')
		self.soft_exit = self.config.getboolean('OptimizationRoutine', 'soft_exit')
		self.save_pvd = self.config.getboolean('OptimizationRoutine', 'save_pvd')

		if self.save_pvd:
			self.state_pvd_list = []
			for i in range(self.shape_form_handler.state_dim):
				if self.shape_form_handler.state_spaces[i].num_sub_spaces() > 0:
					self.state_pvd_list.append([])
					for j in range(self.shape_form_handler.state_spaces[i].num_sub_spaces()):
						self.state_pvd_list[i].append(fenics.File('./pvd/state_' + str(i) + '_' + str(j) + '.pvd'))
				else:
					self.state_pvd_list.append(fenics.File('./pvd/state_' + str(i) + '.pvd'))



	def print_results(self):
		"""Prints the current state of the optimization algorithm to the console.

		Returns
		-------
		None
			see method description

		"""

		if self.iteration == 0:
			output = 'Iteration ' + format(self.iteration, '4d') + ' - Objective value:  ' + format(self.objective_value, '.3e') + \
					 '    Gradient norm:  ' + format(self.gradient_norm_initial, '.3e') + ' (abs) \n '
		else:
			output = 'Iteration ' + format(self.iteration, '4d') + ' - Objective value:  ' + format(self.objective_value, '.3e') + \
					 '    Gradient norm:  ' + format(self.relative_norm, '.3e') + ' (rel)    Mesh Quality: ' + format(self.line_search.mesh_handler.min_quality, '.2f') + ' (rel)    Step size:  ' + format(self.stepsize, '.3e')

		self.output_dict['cost_function_value'].append(self.objective_value)
		self.output_dict['gradient_norm'].append(self.relative_norm)
		self.output_dict['stepsize'].append(self.stepsize)
		self.output_dict['MeshQuality'].append(self.line_search.mesh_handler.min_quality)

		if self.save_pvd:
			for i in range(self.shape_form_handler.state_dim):
				if self.shape_form_handler.state_spaces[i].num_sub_spaces() > 0:
					for j in range(self.shape_form_handler.state_spaces[i].num_sub_spaces()):
						self.state_pvd_list[i][j] << self.shape_form_handler.states[i].sub(j, True), self.iteration
				else:
					self.state_pvd_list[i] << self.shape_form_handler.states[i], self.iteration

		if self.verbose:
			print(output)



	def finalize(self):
		if self.save_results:
			with open('./history.json', 'w') as file:
				json.dump(self.output_dict, file)



	def run(self):
		pass