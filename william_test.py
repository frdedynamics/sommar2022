# Calculator

# Get numbers from user
num1 = float(input("Enter first number: "))
num2 = float(input("Enter second number: "))

# Get input operation from user
operation = input("Enter an operation to perform (+, -, * or /): ")

case = {
    "+": num1 + num2,
    "-": num1 - num2,
    "*": num1 * num2,
    "/": num1 / num2
}

print(case[operation])

input("Press enter to exit")