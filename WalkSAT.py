# test files
	# there are some test files at the bottom of
	# http://people.sc.fsu.edu/~jburkardt/data/cnf/cnf.html
	# (need to redo the input parser for these)
# todo: avoid local minima
	# restart with new random variables if it hasn't found anything for too long
	# probably reset the "too long" counter if you hit a new maximum number of clauses satisfied for that attempt
# todo: gsat version
	# really easy, just delete the "orig" variable and replace it with:
	# sat = sum(1 for o in self.clauses if o.evaluate())

import random

class Boolean:
	def __init__(self, variables, name, inverted=False):
		self.variables = variables
		self.name = name
		self.inverted = inverted

	def get(self):
		return self.inverted != self.variables[self.name]

	def toggle(self):
		self.variables[self.name] = not self.variables[self.name]

	def __str__(self):
		if self.inverted:
			return "!" + self.name
		else:
			return self.name

class CNFClause:
	def __init__(self, vars):
		self.vars = vars

	def evaluate(self):
		ret = False
		for var in self.vars:
			ret = ret or var.get()
		return ret

	def __str__(self):
		return "+".join(str(var) for var in self.vars)

class CNF: #AND of ORs
	def __init__(self, expr):
		self.variables = {}
		self.clauses = []
		for clause in expr.split("*"):
			cl = []
			for var in clause.strip("()").split("+"):
				if var[0] == "!":
					cl.append(Boolean(self.variables, var[1:], True))
					self.variables[var[1:]] = None
				else:
					cl.append(Boolean(self.variables, var))
					self.variables[var] = None
			self.clauses.append(CNFClause(cl))

	def evaluate(self):
		ret = True
		for clause in self.clauses:
			ret = ret and clause.evaluate()
		return ret

	def satisfied(self, rly=True):
		ret = []
		for clause in self.clauses:
			if rly == clause.evaluate():
				ret.append(clause)
		return ret

	def random(self):
		for var in cnf.variables:
			cnf.variables[var] = not random.getrandbits(1)

	def walksat(self):
		self.random()
		while not self.evaluate():
			clause = random.choice(cnf.satisfied(False))
			orig = self.satisfied()
			best_var = []
			best_sat = 0
			for var in clause.vars:
				var.toggle()
				sat = sum(1 for o in orig if o.evaluate())
				if sat > best_sat:
					best_sat = sat
					best_var = [var]
				elif sat == best_sat:
					best_var.append(var)
				var.toggle()
			random.choice(best_var).toggle()
		return True

	def __str__(self):
		return "(" + ")*(".join(str(cl) for cl in self.clauses) + ")"

cnf = CNF("(A+B)*(!B+C+!D)*(D+!E)")
print(cnf)
cnf.walksat()
print(cnf.variables)





# generate a harder test
vars = {}
for v in range(100):
	vars[str(v)] = not random.getrandbits(1)
expr = []
for clause in range(1000):
	cl = []
	attempt = False
	for _ in range(2):
		v = random.choice(list(vars.keys()))
		inv = not random.getrandbits(1)
		cl.append(Boolean(vars, v, inv))
		attempt = attempt or (inv != vars[v])
	if attempt:
		expr.append(cl)
string = "*".join("+".join(str(v) for v in cl) for cl in expr)
cnf = CNF(string)
print(cnf)
print(len(cnf.clauses))
cnf.walksat()
print(cnf.variables)