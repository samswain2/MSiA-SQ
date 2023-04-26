print( 0 / 0 )

# try:
#     print( 0 / 0 )
# except Exception as err:
#     print(f"Unexpected {err=}, {type(err)=}")


# try:
#     f = open('iris.csv')
#     s = f.readline()
#     i = int(s.strip())
# except OSError as err:
#     print("OS error:", err)
# except ValueError:
#     print("Could not convert data to an integer.")
#     #raise
# except Exception as err:
#     print(f"Unexpected {err=}, {type(err)=}")
#     #raise
# finally :
#     print(f"Handled error successfully")