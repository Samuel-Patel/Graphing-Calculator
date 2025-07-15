import numpy as np  # numpy is needed for array processing
import math
from string_conversion import expression_to_function, vector_expression_to_function
# imports expression_to_function for the create_expression function

cartesian_range = {"x": [], "y": []}    # initialises range
polar_range = {"x": [], "y": []}    # here "x" references theta and "y" references r


def get_range(corners):  # corners = [top_left, bottom_right]
    global cartesian_range
    global polar_range

    x_range = [corners[0][0], corners[1][0]]    # range of x vals
    cartesian_range["x"] = x_range
    y_range = [corners[1][1], corners[0][1]]    # range of y vals
    cartesian_range["y"] = y_range

    theta_range = [0, 2*np.pi]  # range of theta vals
    polar_range["x"] = theta_range
    r_max = np.sqrt((x_range[0] - x_range[1])**2 + (y_range[0]-y_range[1])**2) / 2  # gets length of
    # screen diagonal and divides it by 2
    r_range = [-r_max, r_max]    # range of r vals
    polar_range["y"] = r_range


class Expression:  # explicit functions with one variable
    range = None

    def __init__(self, p_function, p_vars):
        self.function = p_function  # sets function and variable parameters
        self.variables = p_vars

    def get_points(self, p_range, num_samples):
        x = np.linspace(p_range[0], p_range[1], num_samples)  # creates array of x values
        # calculates y values
        if len(self.variables) > 0:  # exception for if user enters a constant
            y = self.function(x)   # if function takes parameters they are passed
        else:
            y = self.function() * (x * 0 + 1)
            # otherwise None are passed and the result is multiplied by an array of 1s

        mask = np.logical_not(np.isnan(y) | np.isinf(y))  # validation to get rid of invalid y values
        x = x[mask]
        y = y[mask]
        return x, y   # returns x/y values

    @staticmethod
    def plot_points(canvas, x_coords, y_coords, frame_id, colour):
        x = canvas.plane_to_win_x(x_coords)  # converts x/y coords to window coords
        y = canvas.plane_to_win_y(y_coords)

        canvas.create_line(tuple((x[i], y[i]) for i in range(0, len(x))), tags=("plot", str(frame_id)), fill=colour,
                           width=3)  # pairs up x/y coords and draws the graph
        canvas.__class__.graphs.add(frame_id)  # adds new frame id since new graph is on the plane

    def plot(self, canvas, frame_id, colour):
        x, y = self.get_points(cartesian_range["x"], 500)  # calculates and plots points
        self.plot_points(canvas, x, y, frame_id, colour)


class Mapping:

    def __init__(self, p_functions, p_vars):
        self.function = p_functions  # sets function and variable parameters
        self.variables = p_vars

    def marching_squares(self, p_range, canvas, frame_id, colour):

        x = np.linspace(p_range["x"][0], p_range["x"][1], 240)  # 240 samples
        y = np.linspace(p_range["y"][0], p_range["y"][1], 128)  # 128 samples
        xv, yv = np.meshgrid(x, y)  # creates grid of values to get all combinations of x/y
        condition = self.function[0]
        evaluate = self.function[1]

        mask = condition(xv, yv).astype(int)  # 1 when point is inside the contour and 0 when outside

        for i in range(0, 128 - 1):  # loops through all x and y vals
            for j in range(0, 240 - 1):
                num = mask[i, j] * 8 + mask[i, j + 1] * 4 + mask[i + 1, j] * 2 + mask[i + 1, j + 1] * 1  # binary
                # representation of 4 grid points converted to a decimal number for selection statements
                p1, p2, p3, p4 = None, None, None, None  # intialises points
                if num == 0 or num == 15:  # 0000 or 1111 (completely inside or outside of mapping contour)
                    continue
                # all cases where points are on the border
                elif num == 1 or num == 14:  # 0001 or 1110
                    p1 = self.interpolate(evaluate, (xv[i + 1, j + 1], yv[i + 1, j + 1]), (xv[i + 1, j], yv[i + 1, j]))
                    p2 = self.interpolate(evaluate, (xv[i + 1, j + 1], yv[i + 1, j + 1]), (xv[i, j + 1], yv[i, j + 1]))

                elif num == 2 or num == 13:  # 0010 or 1101
                    p1 = self.interpolate(evaluate, (xv[i + 1, j], yv[i + 1, j]), (xv[i + 1, j + 1], yv[i + 1, j + 1]))
                    p2 = self.interpolate(evaluate, (xv[i + 1, j], yv[i + 1, j]), (xv[i, j], yv[i, j]))

                elif num == 3 or num == 12:  # 0011 or 1100
                    p1 = self.interpolate(evaluate, (xv[i + 1, j], yv[i + 1, j]), (xv[i, j], yv[i, j]))
                    p2 = self.interpolate(evaluate, (xv[i + 1, j + 1], yv[i + 1, j + 1]), (xv[i, j + 1], yv[i, j + 1]))

                elif num == 4 or num == 11:  # 0100 or 1011
                    p1 = self.interpolate(evaluate, (xv[i, j + 1], yv[i, j + 1]), (xv[i, j], yv[i, j]))
                    p2 = self.interpolate(evaluate, (xv[i, j + 1], yv[i, j + 1]), (xv[i + 1, j + 1], yv[i + 1, j + 1]))

                elif num == 5 or num == 10:  # 0101 or 1010
                    p1 = self.interpolate(evaluate, (xv[i, j], yv[i, j]), (xv[i, j + 1], yv[i, j + 1]))
                    p2 = self.interpolate(evaluate, (xv[i + 1, j], yv[i + 1, j]), (xv[i + 1, j + 1], yv[i + 1, j + 1]))

                elif num == 6 or num == 9:  # 0110  need to check center value to see if centre is included
                    centre = condition((xv[i, j] + xv[i + 1, j + 1]) / 2, (yv[i, j] + yv[i + 1, j + 1]) / 2)
                    if (centre and num == 6) or (not centre and num == 9):
                        p1 = self.interpolate(evaluate, (xv[i, j], yv[i, j]), (xv[i + 1, j], yv[i + 1, j]))
                        p2 = self.interpolate(evaluate, (xv[i, j], yv[i, j]), (xv[i, j + 1], yv[i, j + 1]))
                        p3 = self.interpolate(evaluate, (xv[i + 1, j], yv[i + 1, j]),
                                              (xv[i + 1, j + 1], yv[i + 1, j + 1]))
                        p4 = self.interpolate(evaluate, (xv[i + 1, j + 1], yv[i + 1, i + 1]),
                                              (xv[i, j + 1], yv[i, j + 1]))
                    elif (centre and num == 9) or (not centre and num == 6):
                        p1 = self.interpolate(evaluate, (xv[i + 1, j + 1], yv[i + 1, j + 1]),
                                              (xv[i, j + 1], yv[i, j + 1]))
                        p2 = self.interpolate(evaluate, (x[i, j], yv[i, j]), (xv[i, j + 1], yv[i, j + 1]))
                        p3 = self.interpolate(evaluate, (xv[i + 1, j], yv[i + 1, j]),
                                              (xv[i + 1, j + 1], yv[i + 1, j + 1]))
                        p4 = self.interpolate(evaluate, (xv[i, j], yv[i, j]), (xv[i + 1, j], yv[i + 1, j]))

                elif num == 7 or num == 8:  # 0111 or 1000
                    p1 = self.interpolate(evaluate, (xv[i, j], yv[i, j]), (xv[i, j + 1], yv[i, j + 1]))
                    p2 = self.interpolate(evaluate, (xv[i, j], yv[i, j]), (xv[i + 1, j], yv[i + 1, j]))

                if p1 is not None and p2 is not None:  # checks if points have been calculated
                    p1 = canvas.plane_to_win(p1)
                    p2 = canvas.plane_to_win(p2)
                    canvas.create_line((p1, p2), tags=("plot", str(frame_id)), fill=colour, width=3)

                if p3 is not None and p4 is not None:  # checks if points have been calculated
                    p3 = canvas.plane_to_win(p3)    # converts the points into window coordinates and
                    p4 = canvas.plane_to_win(p4)    # draws a line connecting them
                    canvas.create_line((p3, p4), tags=("plot", str(frame_id)), fill=colour, width=3)

        canvas.__class__.graphs.add(frame_id)  # adds new frame id since new graph is on the plane

    def interpolate(self, evaluate, point1, point2):
        try:
            v1 = evaluate(point1[0], point1[1])  # Where vn is pointn evaluated at the implicit function used to
            v2 = evaluate(point2[0], point2[1])  # define the mapping
        except RuntimeError:    # exceptions for invalid values
            return None         # skips point if invalid
        except RuntimeWarning:
            return None
        except ZeroDivisionError:
            return None

        if np.isnan(v1) or np.isnan(v2) or np.isinf(v1) or np.isinf(v2):
            # validation to check if the implicit function is defined at point1/2
            return None

        new_x = point1[0] - v1 / (v2 - v1) * (point2[0] - point1[0])  # interpolates between points
        new_y = point1[1] - v1 / (v2 - v1) * (point2[1] - point1[1])
        new_point = (new_x, new_y)  # returns new point
        return new_point

    def plot(self, canvas, frame_id, colour):
        self.marching_squares(cartesian_range, canvas, frame_id, colour)


class PolarExpression(Expression):

    def __init__(self, p_function, p_vars):
        super(PolarExpression, self).__init__(p_function, p_vars)

    def plot(self, canvas, frame_id, colour):
        theta, r = self.get_points(polar_range["x"], 500)   # evaluates function in polar coords
        x = r * np.cos(theta)  # converting from polar coords to cartesian coords
        y = r * np.sin(theta)
        self.plot_points(canvas, x, y, frame_id, colour)    # plotting the cartesian points


class PolarMapping(Mapping):

    def __init__(self, p_functions, p_vars):
        super(PolarMapping, self).__init__(p_functions, p_vars)

    def interpolate(self, evaluate, point1, point2):
        new_polar_point = super(PolarMapping, self).interpolate(evaluate, point1, point2)  # interpolates between points
        # in polar coordinates
        if new_polar_point is None:  # checks if the new point is valid or not
            return None

        new_theta = new_polar_point[0]
        new_r = new_polar_point[1]
        new_cartesian_point = (new_r * np.cos(new_theta), new_r * np.sin(new_theta))  # converts these polar coords into
        # cartesian coords so they can be plotted
        return new_cartesian_point

    def plot(self, canvas, frame_id, colour):
        self.marching_squares(polar_range, canvas, frame_id, colour)    # passing in polar range to get the mapping
        # points in polar coordinates first before they are converted into cartesian coords


class VectorField:
    def __init__(self, p_function):     # p_function will be [x_component, y_component]
        self.func_x = p_function[0]     # functions for components
        self.func_y = p_function[1]

    def plot(self, canvas, frame_id, colour):
        # loops through all integer x and y values
        for x in range(math.floor(cartesian_range["x"][0]), math.ceil(cartesian_range["x"][1]) + 1):
            for y in range(math.floor(cartesian_range["y"][0]), math.ceil(cartesian_range["y"][1]) + 1):

                try:
                    # gets the x and y components for the output vector
                    x_new, y_new = self.func_x(x, y), self.func_y(x, y)
                    # gets the normalisation factor to keep the vectors displayed the same length
                    normalisation_factor = 0.5 / (x_new ** 2 + y_new ** 2) ** 0.5
                    # checks for invalid values
                    if np.isnan(normalisation_factor) or np.isnan(x_new) or np.isnan(y_new) or np.isinf(x_new) \
                            or np.isinf(y_new) or np.isinf(normalisation_factor):
                        continue  # skips to the next point
                except RuntimeError:  # if one of these errors are encountered the x/y vals are invalid and can't be
                    # plotted
                    continue  # skips to the next point
                except ZeroDivisionError:
                    continue
                except RuntimeWarning:
                    continue

                start_pos = canvas.plane_to_win((x, y))  # gets the start position of the arrow in window coords
                end_pos = [canvas.plane_to_win_x(x + x_new * normalisation_factor),  # gets the end position in window
                           canvas.plane_to_win_y(y + y_new * normalisation_factor)]  # coords

                canvas.create_line((start_pos, end_pos), tags=("plot", str(frame_id)), fill=colour, width=3,
                                   arrow="last")  # draws the arrow for the vector

        canvas.graphs.add(frame_id)  # adds vector field to the set of drawn expressions


def create_expression(text):
    # Parameters for string parsing
    functions = {  # functions here must be in ascending length
        "ln": "np.log", "abs": "np.abs",
        "sin": "np.sin", "cos": "np.cos", "tan": "np.tan",
        "csc": "1/np.sin", "sec": "1/np.cos", "cot": "1/np.tan",
        "sqrt": "np.sqrt",
        "sinh": "np.sinh", "cosh": "np.cosh", "tanh": "np.tanh",
        "arcsin": "np.arcsin", "arccos": "np.arccos", "arctan": "np.arctan",
        "arcsinh": "np.arcsinh", "arccosh": "np.arccosh", "arctanh": "np.arctanh"
    }
    variables = ["r", "θ", "x", "y"]
    constants = {"e": "np.e", "π": "np.pi"}  # constants must also be in ascending length
    numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    operators = ["+", "-", "=", "*", "/", "^"]

    # converts string to dictionary with information used to create an expression object
    expression_token = expression_to_function(text, functions, variables, constants, numbers, operators)
    if expression_token is False:   # checks for valid expression
        return False

    generate_expression = {  # lookup table for expression class    generate_expression["coords"]["class"]
        "cartesian": {"mapping": Mapping, "function": Expression},
        "polar": {"mapping": PolarMapping, "function": PolarExpression}
    }
    # gets correct expression class
    new_expression_class = generate_expression[expression_token["type"]["coords"]][expression_token["type"]["class"]]
    # creates the expression object
    new_expression = new_expression_class(expression_token["function"], expression_token["variables"])

    return new_expression


def create_vector(x, y):
    functions = {  # functions here must be in ascending length
        "ln": "np.log", "abs": "np.abs",
        "sin": "np.sin", "cos": "np.cos", "tan": "np.tan",
        "csc": "1/np.sin", "sec": "1/np.cos", "cot": "1/np.tan",
        "sqrt": "np.sqrt",
        "sinh": "np.sinh", "cosh": "np.cosh", "tanh": "np.tanh",
        "arcsin": "np.arcsin", "arccos": "np.arccos", "arctan": "np.arctan",
        "arcsinh": "np.arcsinh", "arccosh": "np.arccosh", "arctanh": "np.arctanh"
    }
    variables = ["x", "y"]  # vector fields only use x, y
    constants = {"e": "np.e", "π": "np.pi"}  # constants must also be in ascending length
    numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    operators = ["+", "-", "*", "/", "^"]  # no = is required due to all vector fields being explicit

    # creates the components of the vectors
    func_x, func_y = vector_expression_to_function(x, functions, variables, constants, numbers, operators), \
                     vector_expression_to_function(y, functions, variables, constants, numbers, operators)

    # checks if vector components are valid or not
    if not func_x or not func_y:
        return False

    vector_expression = VectorField([func_x, func_y])  # creates vector field object

    return vector_expression


if __name__ == "__main__":
    get_range([[-1, 4], [1, -4]])
    expression = Expression(lambda x: np.sin(x), {"x"})
