from copy import copy


def string_to_list(strng):
    output = []     # creates an empty list and adds the
    for i in strng:  # elements of the string to the
        output.append(i)    # empty list one by one
    return output


def tokenisation(expression_string, key_elements):
    if len(key_elements) == 0:  # checks if the stack is empty, the string has no key elements
        return string_to_list(expression_string)    # returns string converted to a list

    element = key_elements.pop()    # gets element at the top of the stack
    split_string = expression_string.split(sep=element)  # removes the element from the list and returns an
    # list containing the two substrings on either side of the element

    if len(split_string) == 1:  # if the list has one element then the element was not in the string
        return tokenisation(split_string[0], key_elements)  # repeats process with other key elements

    expression_list = []
    for i in range(len(split_string)-1):    # goes through all substrings adding the element between them
        expression_list += tokenisation(split_string[i], copy(key_elements)) + [element]  # adds converted substrings to list
    expression_list += tokenisation(split_string[-1], copy(key_elements))  # goes through last substring
    return expression_list


def expression_format(expression_string, functions, constants):
    string_no_spaces = expression_string.replace(" ", "")  # gets rid of any spaces

    # We need to sort key elements by length since we need to check for longer elements first
    key_elements = sorted(list(constants) + list(functions), key=len)
    return tokenisation(string_no_spaces, key_elements)


if __name__ == "__main__":
    print(expression_format("tanhsincosx", {"sin": 0, "tan": 0, "cos": 0, "tanh": 0, "arcsin": 0}, {"pi": 0, "e": 0}))
