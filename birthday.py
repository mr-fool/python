#Tested using Python 3.3.0
#Version 10 change from recursive to function to no-function
#Lucky number generator 
#Limitation: 
#if the inputs are within the range of the loops, the program will assume your inputs are correct
#Program crashs when the input is not integer 
#Contains the maximum amount of days in a month
Max_Day=[31,28,31,30,31,30,31,31,30,31,30,31] 

#Taking user input
year_input=int(input("Please enter the year of your birth\n"))
month_input=int(input("Please enter the month of your birth, 1-12\n"))
days_input=int(input("Please enter the day of your birth\n"))

#loop control variable
loop_control = 1


#testing the year input
while True:
	
	if year_input <= 0 or year_input > 9999:
		print ("Error in year input")
		year_input=int(input("Please enter the year of your birth\n"))

		
	else:
		exit ('Correct Year Input')
		

#testing the month input
while True:
	
	if month_input <= 0 or month_input > 12:
		print ("Error in month input")
		month_input=int(input("Please enter the month of your birth, 1-12\n"))
	else:
		exit ('Correct Month Input')

#testing the day input
while True:
	
	if (days_input > Max_Day[month_input-1] or days_input < 1): #index is used because the maxmium day in every month is different
		print ("Error in day input") #IndexError	
		days_input=int(input("Please enter the day of your birth\n"))

	else:
		exit ('Correct Day Input')	

#Calculating year lucky number
year = year_input
addyear_first_digit = year % 10
year = year // 10
addyear_second_digit = year % 10
year = year // 10
addyear_third_digit = year % 10
year = year // 10 
addyear_fourth_digit = year % 10
year_result = addyear_first_digit + addyear_second_digit + addyear_third_digit + addyear_fourth_digit
print ("Year:",year_result)
	
#Calculating month lucky number	
month = month_input
addmonth_first_digit = month % 10
month = month // 10
addmonth_second_digit = month % 10
month_result = addmonth_first_digit + addmonth_second_digit
print ("Month:", month_result)

#Calculating day lucky number
day = days_input
addday_first_digit = day % 10
day = day // 10
addday_second_digit = day % 10
day_result = addday_first_digit + addday_second_digit
print ("Day:", day_result)

#Final lucky number
print ("Your lucky number is", year_result + month_result + day_result)


