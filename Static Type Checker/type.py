import re, sys, string

#  Expression class and its subclasses
state = {}
tm = {}

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
	
	#Adapted from example in semantics slides
	def value(self, state): 
		left = self.left.value(state)
		right = self.right.value(state)
		if self.op == "+": 
			return left + right
		if self.op == "-": 
			return left - right
		if self.op == "*": 
			return left * right
		if self.op == "/": 
			return left / right
		if self.op == ">": 
			if left > right: 
				return True
			else: 
				return False
		if self.op == ">=": 
			if left >= right: 
				return True
			else: 
				return False
		if self.op == "<": 
			if left < right: 
				return True
			else: 
				return False
		if self.op == "<=": 
			if left <= right: 
				return True
			if left > right: 
				return False
		if self.op == "==": 
			if left == right: 
				return True
			else: 
				return False
		if self.op == "!=": 
			if left != right: 
				return True
			else: 
				return False
	
	def tipe(self, tm): 
		leftSideType = self.left.tipe(tm)
		rightSideType = self.right.tipe(tm)
		if leftSideType != rightSideType: 
			for element in tm: 
				print(element, tm[element])
			print("Type Error:", leftSideType, "=", rightSideType + "!")
			raise SystemExit
		if self.op == "+" or self.op == "-" or self.op == "/" or self.op == "*": 
			return "number"
		if self.op == "<" or self.op == "<=" or self.op == "==" or self.op == ">" or self.op == ">=" or self.op == "!=" or self.op == "and" or self.op == "or":
			return "boolean"  
		else: 
			for element in tm: 
				print(element, tm[element])
			print("Type Error: Invalid operator, please check and retry")
			raise SystemExit
		

class Number( Expression ):
	def __init__(self, val):
		self.val = int(val)
		
	def __str__(self):
		return str(self.val)
	
	def value(self, state): 
		return self.val
	
	def tipe(self, tm): 
		return "number" 

class String( Expression ):
        def __init__(self, val):
                self.val = val
                
        def __str__(self):
                return str(self.val)
	
        def value(self, state): 
                return self.val
        
class VariableRef( Expression ):
	def __init__(self, ident):
		self.name = ident
                
	def __str__(self):
		return self.name
	
	#Since it doesn't have an immediate integer value, references the state dictionary
	def value(self, state): 
		return state[self.name] 
	
	def tipe(self, tm):
		if self.name in tm: 
			return tm[self.name]
		else: 
			for element in tm: 
				print(element, tm[element])
			print("Type Error:", self.name, "is referenced before being defined!")
			raise SystemExit 
		

#  Statement class and its subclasses
class Statement( object ):
        def __str__(self):
                return ""
            
class Assign( Statement ):
	def __init__(self, var, expr):
		self.var = str(var)
		self.expr = expr
                
	def __str__( self ):
		return "= " + self.var + " " + str(self.expr)
	
	#From the semantics slides
	def meaning(self, state): 
		state[self.var] = self.expr.value(state)
		return state
	
	def tipe(self, tm): 
		if self.var not in tm: 
			tm[self.var] = self.expr.tipe(tm)
		else: 
			if tm[self.var] != self.expr.tipe(tm): 
				for element in tm: 
					print(element, tm[element])
				print("Type Error:", tm[self.var], "=", self.expr.tipe(tm) + "!")
				raise SystemExit
		return


class Block( Statement ):
	def __init__(self, stmts):
		self.stmts = stmts
		
	def __str__(self):
		r = ""
		for s in self.stmts:
			r += str(s) +'\n'
		return r

	def meaning(self, state): 
		for element in self.stmts: 
			element.meaning(state)
			
	def tipe(self, tm): 
		for element in self.stmts: 
			element.tipe(tm)
		return 
			
		
class WhileStmt( Statement ):
	def __init__(self, expr, block):
		self.expr = expr
		self.body = block
		
	def __str__(self):
		return "while " + str(self.expr) + "\n" + str(self.body) + "endwhile"
	
	def meaning(self, state): 
		while self.expr.value(state) == True: 
			self.body.meaning(state)
			
	def tipe(self, tm): 
		if self.expr.tipe(tm) == "boolean": 
			self.body.tipe(tm)
		else: 
			for element in tm: 
				print(element, tm[element])
			print("Type Error: While Statement needs boolean type")
			raise SystemExit
		return 
		

class IfStmt( Statement ):
	
	#Both then and elseblock are block types, self.expr is a binary expression
	def __init__(self, expr, block, elseblock):
		self.expr = expr
		self.then = block
		self.elseblock = elseblock
		    
	def __str__(self):
		return "if " + str(self.expr) + "\n" + str(self.then) + "else\n" + str(self.elseblock) + "endif"
	
	#Checks Boolean value of test expression. Finds meaning of appropriate block of instructions afterward
	def meaning(self, state): 
		if self.expr.value(state) == True: 
			self.then.meaning(state)
		if self.expr.value(state) == False: 
			self.elseblock.meaning(state)
			
	def tipe(self, tm): 
		if self.expr.tipe(tm) == "boolean": 
			self.then.tipe(tm)
			self.elseblock.tipe(tm)
		else: 
			for element in tm: 
				print(element, tm[element])
			print("Type Error: If Statement needs boolean type")
			raise SystemExit
		return 
			
    

debug = False

# aux routine

def error( msg ):
	#print msg
	sys.exit(msg)

def match(matchtok, tokens):
	tok = tokens.peek( )
	if (tok != matchtok): error("Expecting "+matchtok)
	return tokens.next( )

# The "parse" function. This builds a list of tokens from the input string,
# and then hands it to a recursive descent parser for the PAL grammar.

def parseFactor(tokens):
	""" factor -> '(' expr ')' | ident | number | string """
	tok = tokens.peek( )
	if debug: print("Factor: " + str(tok))
	if re.match(Lexer.number, tok):
		tokens.next( )
		return Number(tok)
	if re.match(Lexer.string, tok):
		tokens.next( )
		return String(tok)
	if re.match(Lexer.identifier, tok):
		tokens.next( )
		return VariableRef(tok)
	if tok == "(":
		tokens.next( )
		expr = parseExpr(tokens)
		tok = tokens.peek( )
		if tok != ")":
			error("Missing )");
		tokens.next( )
		return expr
	error("Invalid operand")
	return None

def parseTerm(tokens):
	""" term -> factor { ('*' | '/') factor } """
	tok = tokens.peek( )
	if debug: print("Term: "+str(tok))
	left = parseFactor(tokens)
	tok = tokens.peek( )
	while tok == "*" or tok == "/":
		savetok = tok
		tokens.next()
		right = parseFactor(tokens)
		left = BinaryExpr(savetok, left, right)
		tok = tokens.peek( )
	return left

def parseAddExpr(tokens):
	""" addExpr    = term { ('+' | '-') term } """
	tok = tokens.peek( )
	if debug: print("Expr: "+str(tok))
	left = parseTerm(tokens)
	tok = tokens.peek( )
	while tok == "+" or tok == "-":
		savetok = tok
		tokens.next()
		right = parseTerm(tokens)
		left = BinaryExpr(savetok, left, right)
		tok = tokens.peek( )
	return left

def relExpr(tokens):
	""" relExpr    = addExpr { ('+' | '-') addExpr } """
	tok = tokens.peek( )
	if debug: print("Expr: " +str(tok))
	left = parseAddExpr(tokens)
	tok = tokens.peek( )
	if tok == "<" or tok == "<=" or tok == ">" or tok == ">=" or tok == "==" or tok == "!=":
		savetok = tok
		tokens.next()
		right = parseAddExpr(tokens)
		left = BinaryExpr(savetok, left, right)
		tok = tokens.peek( )
	return left

def andExpr(tokens):
	""" andExpr    = relExpr { 'and' relExpr } """
	tok = tokens.peek( )
	if debug: print ("Expr: "+str(tok))
	left = relExpr(tokens)
	tok = tokens.peek( )
	while tok == "and":
		savetok = tok
		tokens.next()
		right = relExpr(tokens)
		left = BinaryExpr(savetok, left, right)
		tok = tokens.peek( )
	return left

def parseExpr(tokens):
	""" Expr    = andExpr { 'or' andExpr } """
	tok = tokens.peek( )
	if debug: print("Expr: " + str(tok))
	left = andExpr(tokens)
	tok = tokens.peek( )
	while tok == "or":
		savetok = tok
		tokens.next()
		right = andExpr(tokens)
		left = BinaryExpr(savetok, left, right)
		tok = tokens.peek( )
	return left

def parseAssign(tokens):
	""" assign -> ident '=' expr """
	var = tokens.peek( )
	tokens.next( )
	if tokens.peek() == "=":
		match("=", tokens)
		expr = parseExpr(tokens)
		match(";", tokens)
		return Assign(var, expr)
	error("Invalid assignment or function call")
	return None
	
def parseBlock(tokens):
	tok = match("@", tokens)
	stmts = [ ]
	while tok != "~":
		if debug: print("BlocK: "+str(tok))
		stmts.append(parseStmt(tokens))
		if debug: print("Block stmt: " + str(tokens.peek( )))
		tok = tokens.peek( ) # match(";", tokens)
	tokens.next( )
	if debug and tokens.peek() != None: print("End block: " + str(tokens.peek()))
	return Block(stmts)

def parseWhile(tokens):
	""" whileStmt = 'while' expression ':' eoln block """
	tokens.next( )
	expr = parseExpr(tokens)
	match(":", tokens)
	match(";", tokens)
	stmts = parseBlock(tokens)
	return WhileStmt(expr, stmts)

def parseIf(tokens):
	""" ifStmt = 'if' expression ':' eoln block
		[ else ':' eoln block ]  """
	tokens.next( )
	expr = parseExpr(tokens)
	match(":", tokens)
	match(";", tokens)
	stmts = parseBlock(tokens)
	elsestmts = Block([ ])
	if tokens.peek( ) == "else":
		tokens.next( )
		match(":", tokens)
		match(";", tokens)
		elsestmts = parseBlock(tokens)
	return IfStmt(expr, stmts, elsestmts)

def parseStmt(tokens):
	tok = tokens.peek( )
	if debug:
		print("Stmt: "+str(tok))
	if tok == "while":
		return parseWhile(tokens)
	if tok == "if":
		return parseIf(tokens)
	if re.match(Lexer.identifier, tok):
		return parseAssign(tokens)
	return None

def parseStmtList(tokens  ):
	""" gee = { Statement } """
	stmts = [ ]
	tok = tokens.peek( )
	while tok is not None:
		ast = parseStmt(tokens)
		stmts.append(ast)
		if tokens.peek() == ";":
			match(';', tokens)
		tok = tokens.peek();
	return stmts
		

def parse( text ) :
	global tokens
	stateString = "{"
	tokens = Lexer( text )
	stmtlist = parseStmtList( tokens )
	for element in stmtlist: 
		element.tipe(tm)
	for element in tm: 
		print(element, tm[element])

	"""for element in stmtlist: 
		element.meaning(state)
	commaCounter = len(state)
	for element in state: 
		stateString = stateString + "<" + str(element) + ", " + str(state[element]) + ">"
		commaCounter -= 1
		if commaCounter != 0: 
			stateString += ", "		
	stateString += "}"
	print ("\n" + stateString)"""
	return

# Lexer, a private class that represents lists of tokens from a Gee
# statement. This class provides the following to its clients:
#
#   o A constructor that takes a string representing a statement
#       as its only parameter, and that initializes a sequence with
#       the tokens from that string.
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
	
	special = r"\(|\)|\[|\]|,|:|;|@|~|\$"
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




# The following functions form a recursive descent parser for Gee, with the start
# symbol being script.


# "makeString," a utility function that breaks a string constant into a list
# of syntax trees for its individual characters. This list can then be used as
# the elements of an array (since a Gee string is just a shorthand for an array
# of characters). Since the first and last 2 characters of the token are the
# string delimiters, and everything else is meaningful text, this just makes a
# list of "Atomtrees" for everything except those first and last characters.

#def makeString( token ) :
#	return [ AtomTree(c) for c in token[2:-2] ]


#  Main program if called by itself

#def main():
#        """main program for testing"""
#        if len(sys.argv) < 2:
#                print "Usage:  %s filename" % sys.argv[0]
#                return
#        inn = open(sys.argv[1], "r")
#        lines = inn.readlines()
#        parse(string.join(lines, ";"))
#        # print str(ast)
#        return

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
                #print (line.rstrip())
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
                                line = '~ ' + line
                #print(str(ct)+ "\t"+ line)
                lines.append(line)
	# print len(pos)
        undent = ""
        for i in pos[1:]:
                undent += " ~ "
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
		if opt == "-d":
			debug = True
	if len(sys.argv) < 2+ct:
                print ("Usage:  %s filename" % sys.argv[0])
                return
	parse("".join(mklines(sys.argv[1+ct])))
	return


if __name__ == '__main__':
	main()

