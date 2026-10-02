import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from astropy.coordinates import SkyCoord
from tkinter import ttk, Button, Label, Entry, Frame, Checkbutton
import tkinter as tk  
from starplotting import starplotting
import csv
import datetime, calendar
from astroquery.simbad import Simbad

# Test imports

# 

# Set defs and starting params ---------------------------------------------------------------


# Setting the path for where the editable files are grabbed. Thanks apple for forcing me to do this
# When a .app (mac .exe) is clicked, the actual binary that is run is three directories deep in whatever.app/Contents/MacOS/
# So instead, if a mac is detected, move the intended path up to where the .app is
if sys.platform == 'darwin':
    app_dir = os.path.abspath(os.path.join(os.path.dirname(sys.executable), '..', '..', '..'))
else:
    # Have to make a new path for windows and linux too
    app_dir = os.path.dirname(os.path.abspath(__file__))

# Setting open() function path
observer_list_path = os.path.join(app_dir, "observer_list.csv")
target_list_path = os.path.join(app_dir, "target_list.txt")
  


# Setting up the main app window where all other entries will go in
root = tk.Tk()
root.geometry("1300x500")
root.title("Star lookup")

# Load premade observatry list
with open(observer_list_path, newline='') as csvfile:
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
    locationentrywindow.geometry("650x200")
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

    Button(locationentrywindow, text="Add location", command=lambda: addlocation(name, lat, long, el, locationentrywindow)).grid(row=3, column=1)
    


# Adding the location data into the csv file
def addlocation(name, lat, long, el, locationentrywindow):
    with open(observer_list_path, 'a', newline='') as csvfile:
        newlocation = [name.get(), lat.get(), long.get(), el.get()]
        writer = csv.writer(csvfile)
        writer.writerow(newlocation)
        
    # Update the lists used to send the coords to plotting and fill out the dropdown box respectivly
    global observer_locations
    with open(observer_list_path, newline='') as csvfile:
        observer_locations = list(csv.reader(csvfile))
      
    # print(observer_locations)
    global locationnames
    locationnames.append(observer_locations[-1][0])
    dropbox.config(values=locationnames)
    dropbox.current(0)
    
    locationentrywindow.destroy()
    
    
# Selecting the row to omit then rewrite the file without it
def dellocation():   
    # Loading file and putting it in a seperate list
    with open(observer_list_path, "r", newline="") as file:
        csvrows = list(csv.reader(file))
    del csvrows[dropbox.current()]
    
    # Rewriting file with the seperate list minus the deleted file
    with open(observer_list_path, "w", newline="") as rewritecsv:
        writer = csv.writer(rewritecsv)
        for row in csvrows:
            writer.writerow(row)
    
    
    # Update the lists used to send the coords to plotting and fill out the dropdown box respectivly
    global observer_locations
    with open(observer_list_path, newline='') as csvfile:
        observer_locations = list(csv.reader(csvfile))
    
    global locationnames
    del locationnames[dropbox.current()]
    dropbox.config(values=locationnames)
    dropbox.current(0)  
   
    
    
    
# Test is new value is valid, then add to the list and update the gui
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
    with open(target_list_path, newline='') as txtfile:
        # Strip the lines to remove any artifacts. Without this, if more than the starting three targets were plotted,
        # there would be a box appearing at the end of the original starlist targets text
        starlist = [line.strip() for line in txtfile.readlines() if line.strip()]
    starcheckandlist()
    
# When the lookup button is hit, reload the lookup. Test def, should prob fold this into simbadlookup()
def radiobuttonhit():
    print(radioselect.get())
    simbadlookup()

# Def to query simbad for all the strs in "votables". Make sure to update "simbadlookups" as well if altering lookups
def simbadlookup():
    # Used for setting the row
    count = 1
    
    # Starting the simbad query and clearing incase the previous lookup didn't
    s = Simbad()
    s.reset_votable_fields()
    # Looking up all the votables defined by the tuple. Have to use * to seperate each entry
    s.add_votable_fields(*votables)
    # Get the details of the currently selected target and set it to a variable
    simbadquery = s.query_object(radioselect.get())
    
    votablesdict["target"].config(text=radioselect.get())
    for votable in votables:
        count += 1
        # Fill out entries in order of votables tuple. Converting to str and using the last line which gives the wanted value
        votablesdict[votable].config(text=str(simbadquery[votable]).split("\n")[-1]) # = Label(simbadinfoframe, text=str(simbadquery[votable]).split("\n")[-1]).grid(row=count, column=1)
        # For cases empty info, state why that is
        if simbadquery[votable] == "":
            # votablesdict[votable] = Label(simbadinfoframe, text="Not a star").grid(row=count, column=1)
            votablesdict[votable].config(text="Not a star")
        elif str(simbadquery[votable]).split("\n")[-1] == "      --":
            # Label(simbadinfoframe, text="No data").grid(row=count, column=1)
            votablesdict[votable].config(text="No data")
       
        
# Def for freezeing the hover-over annotation when clicking
hover_frozen = {"state": False, "x": None, "y": None}   
 
def toggle_freeze(event):
    if event.inaxes != ax:
        return

    hover_frozen["state"] = not hover_frozen["state"]

    # If freezing, store current position
    if hover_frozen["state"]:
        hover_frozen["x"] = event.xdata
        hover_frozen["y"] = event.ydata

        # copy current hover text into frozen annotation
        ax.frozen_annot.set_text(ax.annot.get_text())
        ax.frozen_annot.xy = (event.xdata, event.ydata)
        ax.frozen_annot.set_visible(True)

    else:
        ax.frozen_annot.set_visible(False)

    canvas.draw_idle()


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
# listframe.configure(bg="white")
starlist = ["M77", "Procyon", "Vega"]


# Variable the radiobox uses to determine both it's initial selection and it's output
radioselect = tk.StringVar(value=starlist[0])

def starcheckandlist():
    # Emptying the frame to repopulate it
    for widget in listframe.winfo_children():
        widget.destroy()    
    
    # Making the labels for each column 
    Label(listframe, text="Display").grid(row=0, column=0)
    Label(listframe, text="Target", bg=targetlistframe.cget("bg")).grid(row=0, column=1)
    Label(listframe, text="Info").grid(row=0, column=2)
    
    for i in range(len(starlist)):        
        # Creating the states of the checkboxes. Could be chenged by .ttk version of Checkbutton
        checkchecklist["checkvar{0}".format(i)] = tk.BooleanVar()
        
        # Creating checkboxes to match the text entries
        checkdict["checkbox{0}".format(i)] = Checkbutton(listframe, variable=checkchecklist['checkvar'+str(i)])
        checkdict["checkbox" + str(i)].grid(row=i+1, column=0)
        checkdict["checkbox" + str(i)].configure(bg="white")
        
    
        # Creating and filling out text entries
        targettext = tk.StringVar(value=starlist[i])
        entrydict["entry{0}".format(i)] = Entry(listframe, textvariable=targettext, state="readonly")
        entrydict["entry" + str(i)].grid(row=i+1, column=1)  
        # entrydict["entry" + str(i)].configure(bg="white")           
        entrydict["entry" + str(i)]["textvariable"] = targettext
        
        
        # Creating linked checkboxes (radiobutton) to choose what target is displaying simbad info
        # radiobuttonvariable = tk.BooleanVar() #Progably need a list matching the target amount?
        tk.Radiobutton(listframe, text="", variable=radioselect, value=starlist[i], command=radiobuttonhit).grid(row=i+1, column=2)
        


# Three column frame for checklist buttons
checklistbuttonsframe = Frame(targetlistframe)


# Button to import targets from a text file
Button(checklistbuttonsframe, text="Import target list", command=importtargets).grid(row=0, column=0, padx=10)

# Button for removing listbox entries
Button(checklistbuttonsframe, text="Remove item", command=delentry).grid(row=0, column=1, padx=10)

# Button for star lookup
Button(checklistbuttonsframe, text="Plot targets", command=starlookup).grid(row=0, column=2, padx=10)

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
xaxismodes = ["UTC", "LST"] # , "Local", 
yaxismodes = ["Altitude", "Parallactic angle", "Airmass"] 
xaxisdropbox = ttk.Combobox(targetlistframe, values=xaxismodes, state='readonly')
yaxisdropbox = ttk.Combobox(targetlistframe, values=yaxismodes, state='readonly')
xaxisdropbox.current(0)
yaxisdropbox.current(0)
xaxisdropbox.grid(row=7, column=0)
yaxisdropbox.grid(row=7, column=1)




#---------------------------------------------------------------------------------------------
# Def for generating the annotation and enlarged plot point
def hover(event):

    if event.inaxes != ax:
        ax.annot.set_visible(False)
        ax.cursor_line.set_visible(False)
        canvas.draw_idle()
        return

    # If the plot is clicked to freeze the annotation, wait till clicked again to resume
    if hover_frozen["state"]:
        return
        mouse_x = hover_frozen["x"]
    else:
        mouse_x = event.xdata



    # Array to store the star names and y-value that will be displayed in the annotation
    text_lines = []
    
    # Find the x and y values of each plot, then add them to text_line for the annotation
    for i, (line, star_name) in enumerate(ax.hover_lines):

        x = np.asarray(line.get_xdata(), dtype=float)
        y = np.asarray(line.get_ydata(), dtype=float)
    
        idx = np.argmin(np.abs(x - mouse_x))
    
        # Star name and y-value that will be added to the annotation text
        text_lines.append(f"{star_name}: {y[idx]:.1f}°")
    
        # Move each star’s enlarged marker to their x and y coords and overwrite plot point
        ax.hover_markers[i].set_offsets([(x[idx], y[idx])])
        ax.hover_markers[i].set_visible(True)

    # Start the annotation text with the time (x-value) then add all the targets y-values
    text = (f"{xaxisdropbox.get()} = {(mouse_x % 24):.2f}\n\n" + "\n".join(text_lines))
    

    ax.annot.set_text(text)

    # Put annotation near top of plot and make it visable
    ax.annot.xy = (event.xdata, event.ydata)
    ax.annot.set_visible(True)
    ax.cursor_line.set_xdata([mouse_x])
    ax.cursor_line.set_visible(True)
    
    canvas.draw_idle()


# Creating and placing the plot to be used later
fig = Figure()
ax = fig.add_subplot(111)

canvas = FigureCanvasTkAgg(fig, root)
canvas.get_tk_widget().pack(side='left', anchor='ne')
fig.canvas.mpl_connect("motion_notify_event", hover)


# Have to make these after "ax" is created
# Making the hover-over label. This will be recreated when a plot is generated so these values aren't too important
ax.annot = ax.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points", bbox=dict(boxstyle="round", fc="w"), annotation_clip=False)
ax.annot.set_visible(False)


# Creating the vertical line for making the hover-over more readable
ax.cursor_line = ax.axvline(color='red', linestyle='--', alpha=0.5)
ax.cursor_line.set_visible(False)

# Empty arrays to prevet errors of hovering over the plot before the first one is drawn
ax.hover_lines = []
ax.hover_markers = []

# Binding clicking to freezing the anootation
canvas.mpl_connect("button_press_event", toggle_freeze)
#------------------------------------------------------------------------------
# Setting up info panel for selected target, starting with a new frame just for the simbad info
simbadinfoframe = Frame(root)

# Listing the votables that will be looked up from simbad
simbadlookups = ('RA', 'Dec', 'Object type', 'Spectral type', 'B mag', 'V mag', 'R mag', 'I mag', 'J mag', 'K mag', 'Proper motion RA', 'Proper motion Dec')
simbadlookupsrow = 2
votables = ('ra', 'dec', 'otype', 'sp_type', 'B', 'V', 'R', 'I', 'J', 'K', 'pmra', 'pmdec')
votablesdict = {}

# Starting row stating the name of the target being shown
Label(simbadinfoframe, text="Target:").grid(row=0, column=0)
Label(simbadinfoframe, text=radioselect.get()).grid(row=0, column=1)


# All the info pulled from simbad
Label(simbadinfoframe, text="Details:").grid(row=1, column=0, columnspan=2)

for label in simbadlookups:
    Label(simbadinfoframe, text=label + ":").grid(row=simbadlookupsrow, column=0)
    simbadlookupsrow += 1


# Used for setting the row
count = 1

# Starting the simbad query and clearing incase the previous lookup didn't
s = Simbad()
s.reset_votable_fields()
# Looking up all the votables defined by the tuple. Have to use * to seperate each entry
s.add_votable_fields(*votables)
# Get the details of the currently selected target and set it to a variable
simbadquery = s.query_object(radioselect.get())

# Display the info of the currently selected target
# Change the name to the corrently selected target
   
# Place the labels for the data from the lookup and putting them into a dict to modify later
votablesdict["target"] = Label(simbadinfoframe, text=radioselect.get())
votablesdict["target"].grid(row=0, column=1) 
for votable in votables:
    count += 1
    # Fill out entries in order of votables tuple. Converting to str and using the last line which gives the wanted value
    votablesdict[votable] = Label(simbadinfoframe, text=str(simbadquery[votable]).split("\n")[-1])
    votablesdict[votable].grid(row=count, column=1)
    # For cases empty info, state why that is
    if simbadquery[votable] == "":
        # votablesdict[votable] = Label(simbadinfoframe, text="Not a star").grid(row=count, column=1)
        votablesdict[votable].config(text="Not a star")
    elif str(simbadquery[votable]).split("\n")[-1] == "      --":
        # Label(simbadinfoframe, text="No data").grid(row=count, column=1)
        votablesdict[votable].config(text="No data")


# simbadlookup()

simbadinfoframe.pack(side='left', anchor='ne')

#------------------------------------------------------------------------------




# Defs to run at the start
starcheckandlist()



# Start program
root.mainloop()











