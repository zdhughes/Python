#Recursive descent parser


import re, sys, string

debug = False
dict = { }
tokens = [ ]


#  Expression class and its subclasses
class Expression( object ):
	def __str__(self):
		return "" 
	
class BinaryExpr( Expression ):
	def __init__(self, op, left, right):
		self.op = op
		self.left = left
		self.right = right
		
	def __str__(self):
		return str(self.op) + " " + str(self.left) + " " + str(self.right)

class Number( Expression ):
	def __init__(self, value):
		self.value = value
		
	def __str__(self):
		return str(self.value)
	
class ident( Expression ): 
	def __init__(self, var):
		self.var = var
	
	def __str__(self):
		return str(self.var)
	
class string( Expression ): 
	def __init__(self, inputString): 
		self.inputString = inputString
		
	def __str__(self): 
		return self.inputString
	
#Establishes the hierarchy for statement subclasses
class Statement( object ): 
	def __str__(self): 
		return ""
	
class whileStatement( Statement ): 
	def __init__(self, left, right):
		self.left = left
		self.right = right
	
	def __str__(self):
		return "while " + str(self.left) + "\n" + str(self.right) + "endwhile"
	
class ifStatement( Statement ): 
	def __init__(self, op, left, right):
		self.op = op
		self.left = left
		self.right = right
	def __str__(self):
		if self.op == "if":
			return "if " + str(self.left) + "\n" + str(self.right) 
		if self.op == "else":
			return str(self.left) + "else" + "\n" + str(self.right) 
		

class assignStmt( Statement ):
	def __init__(self, op, left, right):
		self.op = op
		self.left = left
		self.right = right
		
	def __str__(self):
		return str(self.op) + " " + str(self.left) + " " + str(self.right) 
	
class blockStr( Statement):
	def __init__(self, StmtList):
		self.StmtList = StmtList
		
	def __str__(self):
		returnstr = ''
		for elem in self.StmtList:
			temp = str(elem) 
			returnstr += (temp + "\n")
		return returnstr


def error( msg ):
	#print msg
	sys.exit(msg)

# The "parse" function. This builds a list of tokens from the input string,
# and then hands it to a recursive descent parser for the PAL grammar.

def match(matchtok):
	tok = tokens.peek( )
	if (tok != matchtok): error("Expecting "+ matchtok)
	tokens.next( )
	return tok
	
def factor( ):
	"""factor     = number |  '(' expression ')' """
	#Appropriately modified the logic to ensure that it works properly 
	tok = tokens.peek( )
	if debug: print ("Factor: ", tok)
	if re.match(Lexer.number, tok):
		expr = Number(tok)
		tokens.next( )
		return expr
	elif re.match(Lexer.string, tok):
		expr = string(tok)
		tokens.next( )
		return expr
	elif re.match(Lexer.identifier, tok):
		expr = ident(tok)
		tokens.next( )
		return expr
	if tok == "(":
		tokens.next( )  # or re
		expr = addExpr( )
		tokens.peek( )
		tok = match(")")
		return expr
	error("Invalid operand")
	return

def term( ):
	""" term    = factor { ('*' | '/') factor } """

	tok = tokens.peek( )
	if debug: print ("Term: ", tok)
	left = factor( )
	tok = tokens.peek( )
	while tok == "*" or tok == "/":
		tokens.next()
		right = factor( )
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek( )
	return left

def addExpr( ):
	""" addExpr    = term { ('+' | '-') term } """

	tok = tokens.peek( )
	if debug: print ("addExpr: ", tok)
	left = term( )
	tok = tokens.peek( )
	while tok == "+" or tok == "-":
		tokens.next()
		right = term( )
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek( )
	return left

def expression(): 
	""" expression = andExpr { "or" andExpr } """
	
	#Implemented as a binaryExpr using the "or" as the operator
	tok = tokens.peek()
	if debug: print("expression: ", tok)
	left = andExpr()
	tok = tokens.peek()
	while tok == "or": 
		tokens.next()
		right = term()
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek()
	return left

def andExpr(): 
	""" andExpr    = relationalExpr { "and" relationalExpr } """
	
	#Implemented as a binaryExpr using the "and" as the operator
	tok = tokens.peek()
	if debug: print("andExpr: ", tok)
	left = relationalExpr()
	tok = tokens.peek()
	while tok == "and": 
		tokens.next()
		right = relationalExpr()
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek()
	return left 

def relationalExpr(): 
	""" relationalExpr = addExpr [ relation addExpr ] """
	
	#Implemented as a binaryExpr using a given relational operator as the operator
	tok = tokens.peek()
	if debug: print("relationalExpr: ", tok)
	left = addExpr()
	tok = tokens.peek()
	while tok == "==" or tok == "!=" or tok == "=<" or tok == ">=" or tok == ">" or tok == "<": 
		tokens.next()
		right = addExpr()
		left = BinaryExpr(tok, left, right)
		tok = tokens.peek()
	return left

def assign(): 
	""" assign = ident "=" expression  eoln """
	
	#Functionally mimics the binaryExpr syntax, as the assignment is supposed to be 
	#in Polish
	tok = tokens.peek()
	if debug: print("assign: ", tok)
	left = ident(tok)
	tokens.next()
	tok = tokens.peek()
	op = tok
	tokens.next()
	right = expression()
	left = assignStmt(op, left, right)
	tok = match(";")
	return left

def statement( ):
	""" statement = ifStatement |  whileStatement  |  assign """
	
	#Properly parses statements according to their varieties
	tok = tokens.peek()
	if debug: print("Statement: ", tok)
	if tok == "if":
		stmt = ifStmt()
		return stmt
	elif tok == "while":
		stmt = whileStmt()
		return stmt
	else:
		stmt = assign()
		return stmt
	
def whileStmt( ):
	""" whileStatement = "while"  expression  block """
	
	tok = tokens.peek()
	if debug: print("whileStatement: ", tok)
	tokens.next()
	left = expression()
	right = block()
	stmt = whileStatement(left, right)
	return stmt

def ifStmt( ):
	""" ifStatement = "if" expression block   [ "else" block ] """
	
	tok = tokens.peek()
	if debug: print("ifStatment: ", tok)
	op = tok
	tokens.next()
	left = expression()
	right = block()
	left = ifStatement(op, left, right)
	tok = tokens.peek()
	if tok == "else":
		op = tok
		tokens.next()
		right = block()
		left = ifStatement(op, left, right)
	left = str(left) + "endif"
	return left

def block( ):
	""" block = ":" eoln indent stmtList undent """
	
	#Matches take care of properly moving along the tokens
	tok = tokens.peek()
	if debug: print("block: ", tok)
	tok = match(":")
	tok = match(";")
	tok = match("@")
	tok = tokens.peek()
	stmt = stmtList()
	stmt = blockStr(stmt)
	tok = match("~")
	return stmt

def stmtList( ):
	""" stmtList =  {  statement  } """
	
	tok = tokens.peek()
	if debug: print("stmtList: ", tok)
	listOfStmt = []
	#Deals with undents and end of the program
	while (tok != "~") and (tok is not None):
		stmt = statement( )
		listOfStmt.append(stmt)
		tok = tokens.peek()
	tok = tokens.peek()
	return listOfStmt
	
def parseStmtList(  ):
	""" gee = { Statement } """
	tok = tokens.peek( )
	ast = stmtList( )
	tok = tokens.peek( )
	return ast

def parse( text ) :
	global tokens
	tokens = Lexer( text )
	stmtlist = parseStmtList( )
	for element in stmtlist: 
		print (str(element))
	return


		
		


# Lexer, a private class that represents lists of tokens from a Gee
# statement. This class provides the following to its clients:
#
#   o A constructor that takes a string representing a statement
#       as its only parameter, and that initializes a sequence with
#       the tokens from that string.assignExpr
#
#   o peek, a parameterless message that returns the next token
#       from a token sequence. This returns the token as a string.
#       If there are no more tokens in the sequence, this message
#       returns None.
#
#   o removeToken, a parameterless message that removes the next
#       token from a token sequence.
#
#   o __str__, a parameterless message that returns a string representation
#       of a token sequence, so that token sequences can print nicely

class Lexer :
	
	
	# The constructor with some regular expressions that define Gee's lexical rules.
	# The constructor uses these expressions to split the input expression into
	# a list of substrings that match Gee tokens, and saves that list to be
	# doled out in response to future "peek" messages. The position in the
	# list at which to dole next is also saved for "nextToken" to use.
	
	special = r"\(|\)|\[|\]|,|:|;|@|~|;|\$"
	relational = "<=?|>=?|==?|!="
	arithmetic = "\+|\-|\*|/"
	#char = r"'."
	string = r"'[^']*'" + "|" + r'"[^"]*"'
	number = r"\-?\d+(?:\.\d+)?"
	literal = string + "|" + number
	#idStart = r"a-zA-Z"
	#idChar = idStart + r"0-9"
	#identifier = "[" + idStart + "][" + idChar + "]*"
	identifier = "[a-zA-Z]\w*"
	lexRules = literal + "|" + special + "|" + relational + "|" + arithmetic + "|" + identifier
	
	def __init__( self, text ) :
		self.tokens = re.findall( Lexer.lexRules, text )
		self.position = 0
		self.indent = [ 0 ]
	
	
	# The peek method. This just returns the token at the current position in the
	# list, or None if the current position is past the end of the list.
	
	def peek( self ) :
		if self.position < len(self.tokens) :
			return self.tokens[ self.position ]
		else :
			return None
	
	
	# The removeToken method. All this has to do is increment the token sequence's
	# position counter.
	
	def next( self ) :
		self.position = self.position + 1
		return self.peek( )
	
	
	# An "__str__" method, so that token sequences print in a useful form.
	
	def __str__( self ) :
		return "<Lexer at " + str(self.position) + " in " + str(self.tokens) + ">"



def chkIndent(line):
	ct = 0
	for ch in line:
		if ch != " ": return ct
		ct += 1
	return ct
		

def delComment(line):
	pos = line.find("#")
	if pos > -1:
		line = line[0:pos]
		line = line.rstrip()
	return line

def mklines(filename):
	inn = open(filename, "r")
	lines = [ ]
	pos = [0]
	ct = 0
	for line in inn:
		ct += 1
		line = line.rstrip( )+";"
		line = delComment(line)
		if len(line) == 0 or line == ";": continue
		indent = chkIndent(line)
		line = line.lstrip( )
		if indent > pos[-1]:
			pos.append(indent)
			line = '@' + line
		elif indent < pos[-1]:
			while indent < pos[-1]:
				del(pos[-1])
				line = '~' + line
		print (ct, "\t", line)
		lines.append(line)
	# print len(pos)
	undent = ""
	for i in pos[1:]:
		undent += "~"
	lines.append(undent)
	# print undent
	return lines



def main():
	"""main program for testing"""
	global debug
	ct = 0
	for opt in sys.argv[1:]:
		if opt[0] != "-": break
		ct = ct + 1
		if opt == "-d": debug = True
	if len(sys.argv) < 2+ct:
		print ("Usage:  %s filename" % sys.argv[0])
		return
	parse("".join(mklines(sys.argv[1+ct])))
	return


main()
