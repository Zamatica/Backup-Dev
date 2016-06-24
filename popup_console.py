with open('error.txt', 'r') as error:
    error_pass = str(error.readline())
    input("========== " + error_pass + " ==========")