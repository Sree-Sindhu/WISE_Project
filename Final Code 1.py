import tkinter as tk
from tkinter import messagebox
import math
from PIL import Image, ImageTk
from PIL.Image import Resampling
import folium
import os
import webbrowser

EPS = 1e-9

# Major cities with coordinates
city_coordinates = { 
    "India" : {
    "New Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Bangalore": (12.9716, 77.5946),
    "Kolkata": (22.5726, 88.3639),
    "Chennai": (13.0827, 80.2707),
    "Hyderabad": (17.3850, 78.4867),
    "Pune": (18.5204, 73.8567),
    "Ahmedabad": (23.0225, 72.5714),
    "Surat": (21.1702, 72.8311),
    "Jaipur": (26.9124, 75.7873),
    "Lucknow": (26.8467, 80.9462),
    "Kanpur": (26.4499, 80.3319),
    "Nagpur": (21.1458, 79.0882),
    "Visakhapatnam": (17.6868, 83.2185),
    "Bhopal": (23.2599, 77.4126),
            },  
    "Russia" : {
    "Moscow": (55.7558, 37.6173),
    "Saint Petersburg": (59.9343, 30.3351),
    "Novosibirsk": (55.0084, 82.9357),
    "Yekaterinburg": (56.8389, 60.6057),
    "Nizhny Novgorod": (56.2965, 43.9361),
    "Kazan": (55.8304, 49.0661),
    "Chelyabinsk": (55.1644, 61.4368),
    "Samara": (53.2415, 50.2212),
    "Omsk": (54.9885, 73.3242),
    "Rostov-on-Don": (47.2357, 39.7015),
    "Ufa": (54.7388, 55.9721),
    "Krasnoyarsk": (56.0153, 92.8932),
    "Perm": (58.0104, 56.2294),
    "Voronezh": (51.6608, 39.2003),
    "Volgograd": (48.7080, 44.5133),
    "Vladimir": (56.1291, 40.4070),
    "Tver": (56.8585, 35.9176),
    "Yaroslavl": (57.6261, 39.8845),
    "Kostroma": (57.7670, 40.9269), 
                },
    "USA" : {
    "New York": (40.7128, -74.0060),
    "Los Angeles": (34.0522, -118.2437),
    "Chicago": (41.8781, -87.6298),
    "Houston": (29.7604, -95.3698),
    "Phoenix": (33.4484, -112.0740),
    "Philadelphia": (39.9526, -75.1652),
    "San Antonio": (29.4241, -98.4936),
    "San Diego": (32.7157, -117.1611),
    "Dallas": (32.7767, -96.7970),
    "San Jose": (37.3382, -121.8863),
    "Austin": (30.2672, -97.7431),
    "Jacksonville": (30.3322, -81.6557),
    "Fort Worth": (32.7555, -97.3308),
    "Columbus": (39.9612, -82.9988),
    "Charlotte": (35.2271, -80.8431)
    }
}

class Point:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __sub__(self, p):
        return Point(self.x - p.x, self.y - p.y)

    def __add__(self, p):
        return Point(self.x + p.x, self.y + p.y)

    def __mul__(self, c):
        return Point(self.x * c, self.y * c)

    def __truediv__(self, c):
        return Point(self.x / c, self.y / c)

    def len(self):
        return math.hypot(self.x, self.y)


def dotp(a, b):
    return a.x * b.x + a.y * b.y


def crossp(a, b):
    return a.x * b.y - a.y * b.x


def closest_approach(a, b, p):
    if dotp(b - a, p - a) <= 0:
        return (p - a).len()
    if dotp(a - b, p - b) <= 0:
        return (p - b).len()
    return abs(crossp(b - a, p - a)) / (b - a).len()


def calculate_distance():
    global P1, P2, closest_p1, closest_p2
    closest_p1 = None 
    closest_p2 = None 
    try:
        misha_cities = misha_listbox.curselection()
        nadia_cities = nadia_listbox.curselection()

        if len(misha_cities) < 2 or len(nadia_cities) < 2:
            messagebox.showerror("Error", "Please select at least two cities for both Misha and Nadia.")
            return

        P1 = [Point(*city_coordinates[misha_country_var.get()][misha_listbox.get(i)]) for i in misha_cities]
        P2 = [Point(*city_coordinates[nadia_country_var.get()][nadia_listbox.get(i)]) for i in nadia_cities]

        T1 = [0.0] * len(P1)
        for i in range(1, len(P1)):
            T1[i] = T1[i - 1] + (P1[i] - P1[i - 1]).len()

        T2 = [0.0] * len(P2)
        for i in range(1, len(P2)):
            T2[i] = T2[i - 1] + (P2[i] - P2[i - 1]).len()

        if (P2[-1] - P1[0]).len() > T2[-1] + EPS:
            messagebox.showinfo("Result", "Impossible")
            return

        distance_lower, distance_higher = 0.0, T2[-1]

        while distance_higher - distance_lower > EPS:
            distance = (distance_higher + distance_lower) / 2
            i1, i2 = 0, 0
            success = False
            while i1 + 1 < len(P1) and i2 + 1 < len(P2):
                if T2[i2 + 1] < T1[i1] + distance:
                    i2 += 1
                    continue
                t1 = max(T1[i1] + distance, T2[i2])
                t2 = min(T1[i1 + 1] + distance, T2[i2 + 1])
                assert t1 < t2 + EPS
                v1 = (P1[i1 + 1] - P1[i1]) / (P1[i1 + 1] - P1[i1]).len()
                v2 = (P2[i2 + 1] - P2[i2]) / (P2[i2 + 1]).len()
                p1 = P1[i1] + v1 * (t1 - distance - T1[i1])
                p2 = P2[i2] + v2 * (t1 - T2[i2])
                if closest_approach(p1, p1 + (v1 - v2) * (t2 - t1), p2) <= distance + EPS:
                    success = True
                    closest_p1, closest_p2 = p1, p2
                    break
                if T1[i1 + 1] + distance < T2[i2 + 1]:
                    i1 += 1
                else:
                    i2 += 1

            if success:
                distance_higher = distance
            else:
                distance_lower = distance

        result = (distance_higher + distance_lower) / 2
        show_result_window(P1, P2, result, closest_p1, closest_p2)

    except ValueError:
        messagebox.showerror("Error", "Invalid input! Please enter valid values.")


def show_result_window(P1, P2, result, closest_p1, closest_p2):
    result_window = tk.Toplevel(r)
    result_window.title("Paths and Closest Points")
    result_window.attributes("-fullscreen", True)
    result_window.configure(bg="#FFE4E1")

    result_label = tk.Label(result_window, text=f"Calculated Minimum Distance: {result:.2f}", font=("Arial", 20))
    result_label.pack(pady=10)

    map_path = create_map(P1, P2, closest_p1, closest_p2)

    def open_in_browser():
        webbrowser.open(f"file://{map_path}")

    map_button = tk.Button(result_window, text="Show Map", command=open_in_browser, font=("Arial", 20), bg="#4CAF50", fg="white")
    map_button.pack(pady=10)
    show_animation_button = tk.Button(result_window, text="Show Animation", command=lambda: show_animation(P1, P2), font=("Arial", 16), bg="#4CAF50", fg="white")
    show_animation_button.pack(pady=10)

    tk.Label(result_window, text="Travel is done!", font=("Arial", 20)).pack(pady=10)

    tk.Label(result_window, text="Please rate your experience:", font=("Arial", 20)).pack(pady=10)

    rating = tk.IntVar()
    rating_frame = tk.Frame(result_window)
    rating_frame.pack(pady=10)
    for i in range(1, 6):
        tk.Radiobutton(rating_frame, text=str(i), variable=rating, value=i, font=("Arial", 20)).pack(side=tk.LEFT)

    submit_button = tk.Button(result_window, text="Submit", command=lambda: submit_rating(rating.get()), font=("Arial", 20))
    submit_button.pack(pady=10)

    result_window.update_idletasks()
    width = result_window.winfo_width()
    height = result_window.winfo_height()
    x = (result_window.winfo_screenwidth() // 2) - (width // 2)
    y = (result_window.winfo_screenheight() // 2) - (height // 2)
    result_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

def show_animation(P1, P2):
    print("show_animation() function called")
    animation_window = tk.Toplevel(r)
    animation_window.title("Animation")
    animation_window.attributes("-fullscreen", True)
    animation_window.configure(bg="#FFE4E1")  

    canvas = tk.Canvas(animation_window, width=800, height=600, bg="#FFE4E1")
    canvas.pack()
    canvas = tk.Canvas(animation_window, width=800, height=600, bg="#FFE4E1")
    canvas.pack()

    misha_coords = [(p.x, p.y) for p in P1]
    nadia_coords = [(p.x, p.y) for p in P2]

    # Load images of human figures
    misha_image = Image.open(r"C:\Users\DELL\OneDrive\Desktop\Python\Women.png")
    misha_image = misha_image.resize((50, 100), resample=Resampling.BILINEAR)
    misha_img = ImageTk.PhotoImage(misha_image)
    print("Misha image loaded successfully")

    nadia_image = Image.open(r"C:\Users\DELL\OneDrive\Desktop\Python\Women.png")
    nadia_image = nadia_image.resize((50, 100), resample=Resampling.BILINEAR)
    nadia_img = ImageTk.PhotoImage(nadia_image)
    print("Nadia image loaded successfully")
    
    third_person_image = Image.open(r"C:\Users\DELL\OneDrive\Desktop\Python\Women.png")
    third_person_image = third_person_image.resize((50, 100), resample=Resampling.BILINEAR)
    third_person_img = ImageTk.PhotoImage(third_person_image)
    print("Input image loaded successfully")

    box1 = canvas.create_image(misha_coords[0][0], misha_coords[0][1], image=misha_img)
    box2 = canvas.create_image(nadia_coords[0][0], nadia_coords[0][1], image=nadia_img)
    box3 = canvas.create_image(misha_coords[0][0], misha_coords[0][1], image=third_person_img)

    def animate(index):
        nonlocal box1, box2, box3
        if index < len(misha_coords) - 1:
            canvas.coords(box1, misha_coords[index][0], misha_coords[index][1])
        if index < len(nadia_coords) - 1:
            canvas.coords(box2, nadia_coords[index][0], nadia_coords[index][1])
        if index < len(misha_coords) - 1:
            canvas.coords(box3, misha_coords[index][0], misha_coords[index][1])

    index = 0
    def update_animation():
        nonlocal index
        animate(index)
        index += 1
        if index < len(misha_coords) - 1:
            animation_window.after(500, update_animation)

    update_animation()

    close_button = tk.Button(animation_window, text="Close", command=animation_window.destroy, font=("Arial", 20), bg="#f44336", fg="white")
    close_button.pack(pady=10)

    animation_window.update_idletasks()
    width = animation_window.winfo_width()
    height = animation_window.winfo_height()
    x = (animation_window.winfo_screenwidth() // 2) - (width // 2)
    y = (animation_window.winfo_screenheight() // 2) - (height // 2)
    animation_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

def submit_rating(rating):
    messagebox.showinfo("Rating Submitted", f"Thank you for your rating: {rating}!")


def create_map(P1, P2, closest_p1, closest_p2):
    global my_map, map_path
    center_lat = (sum(p.x for p in P1) + sum(p.x for p in P2)) / (len(P1) + len(P2))
    center_lon = (sum(p.y for p in P1) + sum(p.y for p in P2)) / (len(P1) + len(P2))
    my_map = folium.Map(location=[center_lat, center_lon], zoom_start=6)

    misha_coords = [[p.x, p.y] for p in P1]
    folium.PolyLine(misha_coords, color="blue", weight=2.5, opacity=1).add_to(my_map)
    folium.Marker(misha_coords[0], popup="Misha Start", icon=folium.Icon(color="blue")).add_to(my_map)
    folium.Marker(misha_coords[-1], popup="Misha End", icon=folium.Icon(color="blue")).add_to(my_map)

    nadia_coords = [[p.x, p.y] for p in P2]
    folium.PolyLine(nadia_coords, color="green", weight=2.5, opacity=1).add_to(my_map)
    folium.Marker(nadia_coords[0], popup="Nadia Start", icon=folium.Icon(color="green")).add_to (my_map)
    folium.Marker(nadia_coords[-1], popup="Nadia End", icon=folium.Icon(color="green")).add_to (my_map)

    if closest_p1 and closest_p2:
        folium.Marker([closest_p1.x, closest_p1.y], popup="Closest Point on Misha's Path", icon=folium.Icon(color="red")).add_to (my_map)
        folium.Marker([closest_p2.x, closest_p2.y], popup="Closest Point on Nadia's Path", icon=folium.Icon(color="red")).add_to (my_map)
        folium.PolyLine([[closest_p1.x, closest_p1.y], [closest_p2.x, closest_p2.y]], color="red", weight=2.5, opacity=1).add_to (my_map)

    map_path = os.path.join(os.getcwd(), "map.html")
    my_map.save(map_path)
    return map_path


def start():
    global misha_listbox, nadia_listbox, misha_country_var, nadia_country_var, travel_mode_var
    input_window = tk.Toplevel(r)
    input_window.title("Input Page")
    input_window.attributes("-fullscreen", True)
    input_window.configure(bg="#FFC0CB")

    screen_width = input_window.winfo_screenwidth()
    screen_height = input_window.winfo_screenheight()
    input_width = 800
    input_height = 400
    x_position = (screen_width - input_width) // 2
    y_position = (screen_height - input_height) // 2

    input_window.geometry(f"{input_width}x{input_height}+{x_position}+{y_position}")

    input_label = tk.Label(input_window, text="Select the cities Misha and Nadia traveled:", bg="white", font=("Arial", 16))
    input_label.pack(pady=10)

    country_frame = tk.Frame(input_window, bg="white")
    country_frame.pack(pady=10)

    tk.Label(country_frame, text="Select Misha's Country:", bg="white", font=("Arial", 14)).grid(row=0, column=0)
    misha_country_var = tk.StringVar(value="Russia")
    tk.OptionMenu(country_frame, misha_country_var, "Russia", "India", "USA", command=lambda c: update_city_list(misha_country_var.get(), misha_listbox)).grid(row=0, column=1)

    tk.Label(country_frame, text="Select Nadia's Country:", bg="white", font=("Arial", 14)).grid(row=0, column=2)
    nadia_country_var = tk.StringVar(value="Russia")
    tk.OptionMenu(country_frame, nadia_country_var, "Russia", "India", "USA", command=lambda c: update_city_list(nadia_country_var.get(), nadia_listbox)).grid(row=0, column=3)

    tk.Label(country_frame, text="Select Travel Mode:", bg="white", font=("Arial", 14)).grid(row=1, column=0)
    travel_mode_var = tk.StringVar(value="car")
    tk.OptionMenu(country_frame, travel_mode_var, "Car", "Bus", "Ship", "Flight").grid(row=1, column=1)

    city_frame = tk.Frame(input_window, bg="white")
    city_frame.pack(pady=10)

    misha_listbox = tk.Listbox(city_frame, selectmode=tk.MULTIPLE, exportselection=False, font=("Arial", 14))
    nadia_listbox = tk.Listbox(city_frame, selectmode=tk.MULTIPLE, exportselection=False, font=("Arial", 14))
    
    update_city_list("Russia", misha_listbox)
    update_city_list("Russia", nadia_listbox)

    tk.Label(city_frame, text="Misha's Cities:", bg="white", font=("Arial", 14)).grid(row=0, column=0)
    misha_listbox.grid(row=1, column=0, padx=20, pady=10)

    tk.Label(city_frame, text="Nadia's Cities:", bg="white", font=("Arial", 14)).grid(row=0, column=1)
    nadia_listbox.grid(row=1, column=1, padx=20, pady=10)

    start_button = tk.Button(input_window, text="Calculate Minimum Distance", command=calculate_distance, font=("Arial", 16), bg="#4CAF50", fg="white")
    start_button.pack(pady=10)

    close_button = tk.Button(input_window, text="Close", command=input_window.destroy, font=("Arial", 16), bg="#f44336", fg="white")
    close_button.pack(pady=10)

    input_window.bind("<Escape>", lambda event: input_window.destroy())



def update_city_list(country, listbox):
    listbox.delete(0, tk.END)
    for city in city_coordinates[country]:
        listbox.insert(tk.END, city)


def stop():
    r.destroy()

def load_images():
    global r, russia_img, package_img, russia_image, package_image
    russia_image = Image.open(r"C:\Users\DELL\OneDrive\Desktop\Russia map.png")
    russia_image = russia_image.resize((300, 300), resample=Resampling.BILINEAR)
    russia_img = ImageTk.PhotoImage(russia_image)

    package_image = Image.open(r"C:\Users\DELL\OneDrive\Desktop\Package.png")
    package_image = package_image.resize((300, 300), resample=Resampling.BILINEAR)
    package_img = ImageTk.PhotoImage(package_image)

def gui_step():
    global r, russia_img, package_img
    r = tk.Tk()
    r.title("Messenger")
    r.attributes("-fullscreen", True)
    r.configure(bg="#FFC0CB")

    title_label = tk.Label(r, text="Messenger", font=("Helvetica", 80), bg="#FFC0CB")
    title_label.pack()

    w1 = tk.Label(r, width=80, height=40, bg='#FFC0CB')
    w1.pack(fill=tk.BOTH, expand=True)

    button1 = tk.Button(r, text='Start', width='40', height='10', command=start, bg='green')
    button1.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

    button2 = tk.Button(r, text='Stop', width='40', height='10', command=stop, bg='red')
    button2.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

    load_images()

    russia_label = tk.Label(r, image=russia_img, bg="#FFC0CB")
    russia_label.place(relx=0.25, rely=0.5, anchor=tk.CENTER)

    package_label = tk.Label(r, image=package_img, bg="#FFC0CB")
    package_label.place(relx=0.75, rely=0.5, anchor=tk.CENTER)

    r.mainloop()

gui_step()
