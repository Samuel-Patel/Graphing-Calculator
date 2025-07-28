from list_validation import validate_list, vector_validate_list
import numpy as np  # numpy needs to be imported here as the python functions are generated in this module


def get_type_and_var_set(expression_list, expression_table):
    variable_set = set()    # intialises variable set
    expression_type = {"coords": "", "class": "function"}   # initialises expression's type

    for i in expression_list:
        if expression_table[i] == "variable":   # adds variables to variable set
            variable_set.add(i)
        elif i == "=":  # if there is an equals sign then the expression will be classed as a mapping
            expression_type["class"] = "mapping"

    if "x" in variable_set or "y" in variable_set or len(variable_set) == 0:    # x/y implies cartesian expression
        expression_type["coords"] = "cartesian"

        if expression_type["class"] == "mapping":
            variable_set = ["x", "y"]   # mappings are assigned two variables regardless

    elif "r" in variable_set or "θ" in variable_set:  # r/theta implies polar expression
        expression_type["coords"] = "polar"

        if expression_type["class"] == "mapping":
            variable_set = ["θ", "r"]

    return expression_type, variable_set


def multiplication_convention_removal(expression_list, expression_table):
    output = []  # output expression_list
    prev = None  # last element in expression list

    for i in expression_list:
        if prev is not None:     # prevents using None as a key for the expression_table
            if (expression_table[i] in ["variable", "constant", "function", "open_bracket"]) and \
                    (expression_table[prev] in ["variable", "constant", "number", "closed_bracket"]):
                output.append("*")
            elif expression_table[i] == "number" and expression_table[prev] in ["constant", "variable", "closed_bracket"]:
                output.append("*")  # checks if multiplication symbol is needed by looking at the previous element
                # and adds * to the output list if needed
        output.append(i)    # adds element to the output list
        prev = i    # sets previous element

    # expression table needs to be updated if multiplication signs have been added
    if "*" in output:
        expression_table.update({"*": "operator"})

    return output, expression_table


def function_convention_removal(expression_list, expression_table):
    output = []  # output expression_list
    prev = None  # last element in expression list
    i = 0  # index in expression list for the while loop
    open_bracks = 0

    while i < len(expression_list):

        if prev is not None:  # prevents accessing dictionary with None key
            while expression_table[prev] == "function" and expression_list[i] != "(":
                # looks for functions not followed by an open bracket

                output.append("(")
                open_bracks += 1  # adds the open bracket

                output.append(expression_list[i])
                prev = expression_list[i]  # adds the item to the list and updates pointers
                i += 1

        # in case we encounter a function we also need to make sure that we add brackets after its arguments
            if expression_table[prev] == "function" and expression_list[i] == "(":
                bracket_stack = ["("]

                i += 1
                start = i
                while bracket_stack:
                    if expression_list[i] == ")":
                        bracket_stack.pop()
                    elif expression_list[i] == "(":
                        bracket_stack.append("(")
                    i += 1
                end = i
                output += ["("] + function_convention_removal(expression_list[start:end-1], expression_table)[0] + [")"]

            for j in range(open_bracks):  # adds in the closed brackets to account for the added open brackets
                output.append(")")
            open_bracks = 0  # sets number of open brackets to 0

        if i < len(expression_list):
            output.append(expression_list[i])  # adds item to the list and updates pointers
            prev = expression_list[i]
            i += 1

    # expression table needs to be updated if brackets have been added
    if "(" in output:
        expression_table.update({"(": "open_bracket", ")": "closed_bracket"})


    return output, expression_table


def python_convention_addition(expression_list, expression_table, p_functions, p_constants):
    output = []     # new expression_list
    for i in expression_list:    # iterates through expression list
        if i == "^":    # if the element is not in valid python syntax the Python equivalent is added instead
            output.append("**")  # using a dictionary
        elif expression_table[i] == "function":
            output.append(p_functions[i])
        elif expression_table[i] == "constant":
            output.append(p_constants[i])
        else:
            output.append(i)    # if the item is in valid python syntax it gets added to the new list

    return output


def function_generation(expression_list, variable_set):
    expression_string = "".join(expression_list)    # turns the expression list back into a string to use eval
    var_string = ",".join(list(variable_set))   # turns the variable set into a string with commas separating values

    return eval(f"lambda {var_string}: {expression_string}")


def mapping_generation(expression_list, variable_set):
    for i in range(len(expression_list)):   # iterates through list to find the where the equals sign is

        if expression_list[i] == "=":   # if an equals sign is encountered the string gets converted into the correct
            # form: the condition and the implicit function.
            expression_list_1 = ["("] + expression_list[i+1:] + [") - ("] + expression_list[:i] + [") < 0"]
            expression_list_2 = ["("] + expression_list[i+1:] + [") - ("] + expression_list[:i] + [")"]

            return [function_generation(expression_list_1, variable_set),   # returns both functions
                    function_generation(expression_list_2, variable_set)]


def expression_to_function(expression_string, p_functions, p_variables, p_constants, p_numbers, p_operators):
    # converts string to list and validates the list
    express = validate_list(expression_string, p_functions, p_variables, p_constants, p_numbers, p_operators)
    if express is False:
        return False
    express_type, express_vars = get_type_and_var_set(express["list"], express["table"])

    express["list"], express["table"] = multiplication_convention_removal(express["list"], express["table"])
    express["list"], express["table"] = function_convention_removal(express["list"], express["table"])
    express["list"] = python_convention_addition(express["list"], express["table"], p_functions, p_constants)
    # gets rid of any mathematical conventions that do not agree with python syntax and converts the elements in the
    # list to python syntax

    if express_type["class"] == "mapping":  # depending on the type of expression the python function generated will
        func = mapping_generation(express["list"], express_vars)    # be different
        # [condition, implicit function]
    else:
        func = function_generation(express["list"], express_vars)   # explicit function

    return {"function": func, "type": express_type, "variables": express_vars}


def vector_expression_to_function(expression_string, p_functions, p_variables, p_constants, p_numbers, p_operators):
    # the expression string here is a component of a vector
    # converts string into a validated list and also creates a lookup table for elements
    express = vector_validate_list(expression_string, p_functions, p_variables, p_constants, p_numbers, p_operators)

    if express is False:    # checks for invalid expressions
        return False

    express_vars = ["x", "y"]   # these are the only variables that will be passed for all vectors

    express["list"], express["table"] = multiplication_convention_removal(express["list"], express["table"])
    express["list"], express["table"] = function_convention_removal(express["list"], express["table"])
    express["list"] = python_convention_addition(express["list"], express["table"], p_functions, p_constants)
    # gets rid of any mathematical conventions that do not agree with python syntax and converts the elements in the
    # list to python syntax

    func = function_generation(express["list"], express_vars)   # generates the function for the given vector component

    return func  # returns the Python function used to generate a vector Field object


if __name__ == "__main__":
    functions = {
        "ln": "np.log",
        "sin": "np.sin", "cos": "np.cos", "tan": "np.tan",
        "csc": "1/np.sin", "sec": "1/np.cos", "cot": "1/np.tan",
        "sinh": "np.sinh", "cosh": "np.cosh", "tanh": "np.tanh",
        "arcsin": "np.arcsin", "arccos": "np.arccos", "arctan": "np.arctan",
        "arcsinh": "np.arcsinh", "arccosh": "np.arccosh", "arctanh": "np.arctanh"
    }
    variables = ["r", "θ", "x", "y"]
    constants = {"e": "np.e", "pi": "np.pi"}
    numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    operators = ["+", "-", "=", "*", "/", "^"]
    pstring = "sintancos(x)"

    print(expression_to_function(pstring, functions, variables, constants, numbers, operators))
