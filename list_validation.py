from list_conversion_algorithms import expression_format


def illegal_character_check(expression_list, functions, variables, constants, numbers, operators):
    # goes through all elements in the list and checks if the element is an invalid character
    for i in expression_list:
        if i not in list(functions) + list(variables) + list(constants) + list(numbers) + list(operators) + ["(", ")",
                                                                                                             "."]:
            return False

    return True


def create_lookup_table(expression_list, functions, variables, constants, numbers, operators):
    output = {}     # empty lookup table
    for i in expression_list:   # goes through list and adds key value pairs to the dictionary
        if i in list(functions):        # each key value pair is in the form {"element": "type of element"}
            output.update({i: "function"})
        elif i in list(variables):
            output.update({i: "variable"})
        elif i in list(constants):
            output.update({i: "constant"})
        elif i in list(operators):
            output.update({i: "operator"})
        elif i in list(numbers):
            output.update({i: "number"})
        elif i == ".":
            output.update({i: "decimal_point"})
        elif i == "(":
            output.update({i: "open_bracket"})
        elif i == ")":
            output.update({i: "closed_bracket"})

    return output   # returns lookup table


def bracket_parsing(expression_sublist):
    open_bracks = 0  # number of open brackets without a corresponding closed bracket

    for i in expression_sublist:    # goes through sublist
        if i == "(":    # if an open bracket is encountered then the
            open_bracks += 1    # number of open brackets without a closed bracket is increased

        if i == ")":
            open_bracks -= 1    # if a closed bracket is encountered the number decreases
            if open_bracks < 0:  # checks if there are more closed brackets than closed brackets
                return False

    if open_bracks > 0:  # checks if there are more open brackets than closed brackets
        return False

    return True


def bracket_check(expression_list):
    if "=" in expression_list:  # checks if there is an "=" in the expression
        for i in range(len(expression_list)):    # finds the position of
            if expression_list[i] == "=":   # the equals sign and validates the brackets of both sides of the expression
                return bracket_parsing(expression_list[:i]) and bracket_parsing(expression_list[i+1:])
    else:
        return bracket_parsing(expression_list)  # validates the brackets of the expression if there are no
        # equals signs


def equals_check(expression_list):
    num_of_equals = 0
    for i in expression_list:   # goes through list and find number of equals signs
        if i == "=":
            num_of_equals += 1

    if num_of_equals > 1:   # if there are more than one equals signs then the expression is
        return False    # invalid
    return True


def operator_check(expression_list, expression_table):  # VV having a minus sign at the start of the expression is fine
    if (expression_table[expression_list[0]] == "operator" and expression_list[0] != "-") or \
       (expression_table[expression_list[-1]] == "operator") or (expression_table[expression_list[-1]] == "function") \
            or not equals_check(expression_list):  # checks if there are invalid operators at the start or end of the
        return False  # expression or if there is a function at the end of the expression or if there is more than one
        # equals sign

    prev = None  # previous element
    for i in expression_list:   # goes through expression list
        # checks if the current element is an operator that is not "-" and if the previous element is an operator
        # function or open bracket, in which case the expression is invalid
        if (expression_table[i] == "operator" and i != "-") and expression_table[prev] in \
                ["operator", "function", "open_bracket"]:
            return False
        prev = i    # updates the previous element
    return True


def variable_check(expression_list, expression_table):
    variable_set = set()  # set of all variables in the expression
    equals = False  # condition for if there is an equals sign in the expression or not
    for i in expression_list:   # goes through expression list
        if expression_table[i] == "variable":
            variable_set.add(i)   # adds variables encountered to variable set
        elif i == "=":
            equals = True   # checks if an equals is in the expression

    if 0 < len(variable_set) <= 2 and equals:   # checks if there is a valid number of variables and
        # if the expression is a mapping
        if len(variable_set) == 2 and (("x" in variable_set and "y" in variable_set) or ("r" in variable_set and "θ" in
                                                                                         variable_set)):
            return True     # checks if the two variables in the expression are valid
        elif len(variable_set) == 1:
            return True    # if there is only one variable the expression must be valid

    elif (len(variable_set) == 0 and not equals) or (len(variable_set) == 1 and
                                                     ("x" in variable_set or "θ" in variable_set)):
        # if the expression is an explicit function then it must have an input variable x/θ
        return True

    return False


def validate_list(expression_string, functions, variables, constants, numbers, operators):
    if len(expression_string) < 1:  # checks for an empty string
        return False

    # converts string into the correct format for string parsing
    expression_list = expression_format(expression_string, functions, constants)
    if not illegal_character_check(expression_list, functions, variables, constants, numbers, operators):
        return False    # checks if there are illegal characters in the expression list

    # creates a lookup table for the rest of the string validation
    table = create_lookup_table(expression_list, functions, variables, constants, numbers, operators)

    # checks if the expression obeys the rules of mathematics
    if not bracket_check(expression_list) or not operator_check(expression_list, table) or not \
            variable_check(expression_list, table):
        return False

    # returns the expression list and lookup table
    return {"list": expression_list, "table": table}


def vector_validate_list(expression_string, functions, variables, constants, numbers, operators):
    if len(expression_string) < 1:
        return False

    tokenised_list = expression_format(expression_string, functions, constants)

    if not illegal_character_check(tokenised_list, functions, variables, constants, numbers, operators):
        return False

    table = create_lookup_table(tokenised_list, functions, variables, constants, numbers, operators)

    if not bracket_check(tokenised_list) or not operator_check(tokenised_list, table):
        return False

    return {"list": tokenised_list, "table": table}


if __name__ == "__main__":
    pfunctions = {"sin": 0, "tan": 0, "cos": 0, "arcsin": 0}
    pvariables = ["r", "theta", "x", "y"]
    pconstants = {"pi": 0, "e": 0}
    poperators = ["+", "-", "=", "*", "/"]
    pnumbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    pe_list = ["(", "-", "x", ")"]
    # print(illegal_character_check(pe_list, pfunctions, pvariables, pconstants, pnumbers, poperators))
    table = create_lookup_table(pe_list, pfunctions, pvariables, pconstants, pnumbers, poperators)
    print(table)
    print(operator_check(pe_list, table))
