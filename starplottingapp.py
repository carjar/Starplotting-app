# import numpy as np
# import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import astropy.units as u
from astropy.coordinates import SkyCoord
from tkinter import ttk, Button, Label, Entry, Frame, Checkbutton
import tkinter as tk  
from starplotting import starplotting
import csv
import datetime, calendar

# Test imports

# 

# Set starting params and defs ---------------------------------------------------------------

root = tk.Tk()
root.geometry("1000x600")
root.title("Star lookup")

# Load premade observatry list
with open('observer_list.csv', newline='') as csvfile:
    observer_locations = list(csv.reader(csvfile))


# Def for star lookup
def starlookup():
    star_names = [] # Previously "star_name"
    star_coords = [] # Previously "star"
    for i in range(len(starlist)):
        if checkchecklist["checkvar" + str(i)].get() == True:
            try: # Testing for valid target name if an invalid target somehow ends up in the list         
                SkyCoord.from_name(starlist[i])
            except:
                print("Target not a valid lookup")
                # star = 0
                starlookuplabel.config(text="Target is not valid") # Make the label below the bottom not valid
                continue
            
            # New method of adding multiple stars
            star_names.append(starlist[i])
            star_coords.append(SkyCoord.from_name(starlist[i]))
    
    # Grabbing currently selected location's coords to send to plotting
    observer_coords = []
    observer_coords.append(observer_locations[dropbox.current()])
    
    # Grabbing currently selected date to send to plotting
    observer_date = yearstr.get() + '-' + str(month.current() + 1) + '-' + str(day.current() + 1)
    
    # Grabbing curretly selected plot axis choices
    plot_axes = []
    plot_axes.append(xaxisdropbox.current())
    plot_axes.append(yaxisdropbox.current())
    
    # Making plot
    starplotting(ax, canvas, star_names, star_coords, observer_coords, observer_date, plot_axes)



# Popup window to add a new location to the local observer_list.csv
def coordsentrywin():
    locationentrywindow = tk.Toplevel(root)
    locationentrywindow.geometry("1050x200")
    locationentrywindow.title("Add location")
    root.resizable(False, False)
    
    Label(locationentrywindow, text="Enter the details of the location you wish to add").grid(row=0, column=1)
    Label(locationentrywindow, text="Name").grid(row=1, column=0)
    Label(locationentrywindow, text="Latitude").grid(row=1, column=1)
    Label(locationentrywindow, text="Longitude").grid(row=1, column=2)
    Label(locationentrywindow, text="Elevation (m)").grid(row=1, column=3)
    
    name = Entry(locationentrywindow, textvariable="")
    lat = Entry(locationentrywindow, textvariable="")
    long = Entry(locationentrywindow, textvariable="")
    el = Entry(locationentrywindow, textvariable="")
    
    name.grid(row=2, column=0)
    lat.grid(row=2, column=1)
    long.grid(row=2, column=2)
    el.grid(row=2, column=3)

    Button(locationentrywindow, text="Add location", command=lambda: addlocation(name, lat, long, el)).grid(row=3, column=1)



# Adding the location data into the csv file
def addlocation(name, lat, long, el):
    with open('observer_list.csv', 'a', newline='') as csvfile:
        newlocation = [name.get(), lat.get(), long.get(), el.get()]
        writer = csv.writer(csvfile)
        writer.writerow(newlocation)
        
    # Update the lists used to send the coords to plotting and fill out the dropdown box respectivly
    global observer_locations
    with open('observer_list.csv', newline='') as csvfile:
        observer_locations = list(csv.reader(csvfile))
      
    # print(observer_locations)
    global locationnames
    locationnames.append(observer_locations[-1][0])
    dropbox.config(values=locationnames)
    dropbox.current(0)
    
    
# Selecting the row to omit then rewrite the file without it
def dellocation():   
    # Loading file and putting it in a seperate list
    with open("observer_list.csv", "r", newline="") as file:
        csvrows = list(csv.reader(file))
    del csvrows[dropbox.current()]
    
    # Rewriting file with the seperate list minus the deleted file
    with open("observer_list.csv", "w", newline="") as rewritecsv:
        writer = csv.writer(rewritecsv)
        for row in csvrows:
            writer.writerow(row)
    
    
    # Update the lists used to send the coords to plotting and fill out the dropdown box respectivly
    global observer_locations
    with open('observer_list.csv', newline='') as csvfile:
        observer_locations = list(csv.reader(csvfile))
    
    global locationnames
    del locationnames[dropbox.current()]
    dropbox.config(values=locationnames)
    dropbox.current(0)  
    
    

    
    
    
    
# It prints the current value of the variable.
def addentry(event):
        # print(event)
        try: # Testing for valid target name          
            SkyCoord.from_name(textcontents.get())
        except:
            print("Target not a valid lookup")
            starlookuplabel.config(text="Target is not valid") # Make the label below the bottom not valid   
        else:
            # print("Added to list:", textcontents.get())      
            starlist.append(textcontents.get())
            starcheckandlist()
        
        
# Def for deleting listbox entries
def delentry():
    # starlist.remove(starlistbox.get(ACTIVE))
    delcount = 0
    for i in range(len(starlist)):
        # print(str(checkchecklist["checkvar" + str(i)].get()) + ", checkbox " + str(i))
        if checkchecklist["checkvar" + str(i)].get() == True:
            del starlist[i - delcount]
            delcount = delcount + 1
    starcheckandlist()   
    # return starlist
  


# Import a target list from a text file and remake the target list
def importtargets():
    global starlist
    with open('target_list.txt', newline='') as txtfile:
        starlist = txtfile.readlines()    
    starcheckandlist()
    
      

       

# Gui items ----------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------

# Creating a high level frame to organize all of the interactable elements with the target list
targetlistframe = Frame(root)
targetlistframe.pack(side='left', anchor='nw', padx=3)

# Entry box for adding targets to the listbox and explination
targetentrylabel = Label(targetlistframe, text="Hit Enter to add")
targetentrylabel.grid(row=0, column=0)
textentry = Entry(targetlistframe)
textentry.grid(row=0, column=1)   # Not sure I pack this here or after setting up the variable
textcontents = tk.StringVar()
# textcontents.set("Type target here then hit enter")
textentry["textvariable"] = textcontents



# Listing the stars, with an entry box beside a checkbox each time
# Setting up dicts for the target list --------------
checkdict = {}
entrydict = {}
checkchecklist = {}


# Creating frame for the checkboxes and entries to line up beside each other

listframe = Frame(targetlistframe)
listframe.grid(row=1, column=0, columnspan=2)
listframe.configure(bg="white")
starlist = ["M77", "Procyon", "Vega"]
def starcheckandlist():
    # Emptying the frame to repopulate it
    for widget in listframe.winfo_children():
        widget.destroy()
    # print("sarcheckandlist run")
    # if     
    
    for i in range(len(starlist)):        
        # Creating the states of the checkboxes. Could be chenged by .ttk version of Checkbutton
        checkchecklist["checkvar{0}".format(i)] = tk.BooleanVar()
        
        # Creating checkboxes to match the text entries
        checkdict["checkbox{0}".format(i)] = Checkbutton(listframe, variable=checkchecklist['checkvar'+str(i)])
        checkdict["checkbox" + str(i)].grid(row=i, column=0)
        checkdict["checkbox" + str(i)].configure(bg="white")
        
    
        # Creating and filling out text entries
        targettext = tk.StringVar(value=starlist[i])
        entrydict["entry{0}".format(i)] = Entry(listframe, textvariable=targettext, state="readonly")
        entrydict["entry" + str(i)].grid(row=i, column=1)              
        entrydict["entry" + str(i)]["textvariable"] = targettext
        
    # return check_var, checkdict


# Three column frame for checklist buttons
checklistbuttonsframe = Frame(targetlistframe)


# Button to import targets from a text file
Button(checklistbuttonsframe, text="Import target list", command=importtargets).grid(row=0, column=0, padx=10)

# Button for removing listbox entries
Button(checklistbuttonsframe, text="Remove item", command=delentry).grid(row=0, column=1, padx=10)

# Button for star lookup
Button(checklistbuttonsframe, text="Get object coords", command=starlookup).grid(row=0, column=2, padx=10)

checklistbuttonsframe.grid(row=2, column=0, columnspan=2)



# Label saying if the added target is valid
starlookuplabel = Label(targetlistframe, text=" ")
starlookuplabel.grid(row=3, column=0, columnspan=2)


# Add the entry to the listbox from the textentry when hitting enter    
textentry.bind('<Key-Return>', addentry)




# --------------------------------------------------------------------------------------------
# Creating a different frame that has 3 columns for choosing locations and dates
dateframe = Frame(targetlistframe)

# Adding location to the dateframe for convience
# Needed to make another frame cuz I needed 4 columns fml
locationframe = Frame(targetlistframe)
# Trying adding a dropdown box for locaions
locationnames = []
for i in range(len(observer_locations)):
    locationnames.append(observer_locations[i][0])
    
dropbox = ttk.Combobox(locationframe, values=locationnames, state='readonly')
dropbox.current(0)

Label(locationframe, text="Select location:").grid(row=0, column=0)
dropbox.grid(row=0,column=1)
Button(locationframe, text="Add location", command=coordsentrywin).grid(row=0, column=2)
Button(locationframe, text="Remove location", command=dellocation).grid(row=0, column=3)

locationframe.grid(row=4, column=0, columnspan=2)


# Creating a callable def to change the day list based on what month is selected to avoid error possibilities with invalid dates
day = ttk.Combobox(dateframe, state='readonly')
def daydropdowns(event=None):
    # Get correct number of days for month/year using calendar
    days = calendar.monthrange(int(year.get()), int(month.get()))[1]    
    day['values'] = list(range(1, days + 1))
    day.current(0)
        
    


# Generating variables for the date entries to be read
yearstr = tk.StringVar(value=datetime.date.today().strftime('%Y'))
year = Entry(dateframe, textvariable=yearstr)

# monthstr = tk.StringVar(value=datetime.date.today().strftime('%m'))
monthnumbers = list(range(1,13))
month = ttk.Combobox(dateframe, values=monthnumbers, state='readonly')
month.current(int(datetime.date.today().strftime('%m')) - 1)

    


# When the month is changed, update the days that can be selected
month.bind('<<ComboboxSelected>>', daydropdowns)


# Assigning the labels to the dates and placing them in their own frame
Label(dateframe, text="Year").grid(row=0, column=0)
Label(dateframe, text="Month").grid(row=0, column=1)
Label(dateframe, text="Day").grid(row=0, column=2)
year.grid(row=1, column=0)
month.grid(row=1, column=1)
day.grid(row=1, column=2)

daydropdowns()
day.current(datetime.date.today().day - 1) # Start the day selected at the current one

# Placing the frame where the date imputs are into the interactable frame
dateframe.grid(row=5, column=0, columnspan=2, pady=20)



# Labels to describe what the axes choices are
Label(targetlistframe, text="Time").grid(row=6, column=0)
Label(targetlistframe, text="Y Axis").grid(row=6, column=1)


# Dropboxes to choose the axes of the plot
xaxismodes = ["UTC"] # , "Local", "LST"
yaxismodes = ["Altitude", "Parallactic angle"] # , "Airmass"
xaxisdropbox = ttk.Combobox(targetlistframe, values=xaxismodes, state='readonly')
yaxisdropbox = ttk.Combobox(targetlistframe, values=yaxismodes, state='readonly')
xaxisdropbox.current(0)
yaxisdropbox.current(0)
xaxisdropbox.grid(row=7, column=0)
yaxisdropbox.grid(row=7, column=1)




#---------------------------------------------------------------------------------------------

# Creating the plot to be used later
fig = Figure()
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, root)
canvas.get_tk_widget().pack(side='right', anchor='ne')
# canvas.get_tk_widget().grid(row=6, column=1)
# canvas.get_tk_widget().place(x=300, y=0)


#------------------------------------------------------------------------------
# Setting up the popup window for adding new locations
# locationentrywindow = tk.Tk()
# # locationentrywindow.geometry("500x200")
# locationentrywindow.title("Add location")
# # locationentrywindow.resizable(False, False)

# Label(locationentrywindow, text="Enter the details of the location you wish to add").grid(row=0, column=1)
# Label(locationentrywindow, text="Name").grid(row=1, column=0)
# Label(locationentrywindow, text="Latitude").grid(row=1, column=1)
# Label(locationentrywindow, text="Longitude").grid(row=1, column=2)
# Label(locationentrywindow, text="Elevation (m)").grid(row=1, column=3)

# name = Entry(locationentrywindow, textvariable="")
# lat = Entry(locationentrywindow, textvariable="")
# long = Entry(locationentrywindow, textvariable="")
# el = Entry(locationentrywindow, textvariable="")

# name.grid(row=2, column=0)
# lat.grid(row=2, column=1)
# long.grid(row=2, column=2)
# el.grid(row=2, column=3)

# Button(locationentrywindow, text="Add location", command=addlocation).grid(row=3, column=1)
#------------------------------------------------------------------------------





# Defs to run at the start
starcheckandlist()



# Start program
root.mainloop()











