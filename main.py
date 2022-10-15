import csv
import time
from datetime import datetime
from screeninfo import get_monitors

import kivy
from kivy.app import App
from kivy.app import runTouchApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import NumericProperty

from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.dropdown import DropDown
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout

kivy.require('2.1.0')
cx, cy = Window.size # pobranie wymiarów, aby wyświetlić elementy relatywnie
if cx > cy: # ustawia wymiary okna na maksymalne-250 w obu wymiarach dla monitorów szerszych niż wyższych
	cx, cy = get_monitors()[0].width-250, get_monitors()[0].height-250
	Window.size = (cx, cy)

Window.top = 35
Window.left = 5

class Screen(FloatLayout):
	global cx, cy
	Builder.load_string("""
<Screen>:
	inside:inside # python self.name : kvname
	out:out
	FloatLayout:
		size:root.size
		Label:
			id:inside
			text:"Klienci na siłowni:"
			size_hint: 0.2, 0.1
			pos_hint:{"""+f"'x':{10/cx}, 'y':{(cy-(0.1 * cy)-30)/cy}"+"""}
			canvas.before:
				Color:
					rgba: 100/255, 100/255, 100/255,1
				Rectangle:
					pos: self.pos
					size: self.size
		Label:
			id:out
			text:"Klienci poza siłownią:"
			size_hint: 0.2, 0.1
			pos_hint:{"""+f"'x':{((0.2 * cx) + 30)/cx}, 'y':{(cy-(0.1 * cy)-30)/cy}"+"""}
			canvas.before:
				Color:
					rgba: 100/255, 100/255, 100/255,1
				Rectangle:
					pos: self.pos
					size: self.size""")
	pass
class Drop(FloatLayout):
	global cx, cy
	Builder.load_string("""
<MySlide@Slider>:
	Label:
		pos: (root.value_pos[0] - sp(16), root.center_y - sp(27)) if root.orientation == 'horizontal' else (root.center_x - sp(27), root.value_pos[1] - sp(16))
		size_hint: None, None
		size: sp(32), sp(32)
		font_size: 14
		text: "Dni: "+str(int(root.value)//24)
<Drop>:
	hours:hours
	select:select
	slider:slider
	new:new
	FloatLayout:
		Button:
			id:hours
			text:"Dokup godziny"
			size_hint: 0.25, 0.1
			pos_hint:{"""+f"'x':0.48, 'y':{(cy-(0.2 * cy)-50)/cy}"+"""}
			canvas.before:
				Color:
					rgba: 100/255, 100/255, 100/255,1
				Rectangle:
					pos: self.pos
					size: self.size
		Button:
			id:new
			text:"Dodaj nowego klienta"
			size_hint: 0.25, 0.1
			pos_hint:{"""+f"'x':0.48, 'y':{(cy-(0.4 * cy))/cy}"+"""}
			canvas.before:
				Color:
					rgba: 100/255, 100/255, 100/255,1
				Rectangle:
					pos: self.pos
					size: self.size
		Button:
			id:select
			text:'Wybierz klienta:'
			size_hint: 0.23, 0.1
			pos_hint:{"""+f"'x':0.75, 'y':{(cy-(0.2 * cy)-50)/cy}"+"""}
			canvas.before:
				Color:
					rgba: 100/255, 100/255, 100/255,1
				Rectangle:
					pos: self.pos
					size: self.size
		MySlide:
			id:slider
			min: 24
			max: 744
			step: 24
			size_hint: 0.5, 0.1
			pos_hint: {'x':0.48, 'y':0.86}
			canvas.before:
				Color:
					rgba: 100/255, 100/255, 100/255,1
				Rectangle:
					pos: self.pos
					size: self.size
""")
class Main(FloatLayout):
	def __init__(self, **kwargs):
		global cy
		global cx
		super(Main, self).__init__(**kwargs)
		self.screen = Screen()
		self.drop = Drop()

		self.dropdown = DropDown()
		self.add_widget(self.screen)
		self.add_widget(self.drop)

		self.user = []
		self.inside = {}
		self.clients = {}
		self.out_widgets = []
		self.inside_widgets = []
		self.new_client_popup = None

		self.height = Window.height
		self.drop.new.bind(on_press=self.add_new_guy)

		self.get_csv()
		self.display()
		self.create_time_menu()
	def display(self):
		global cy
		global cx
		i, j = 0, 0
		for x in self.clients.keys():
			if i == 0 and j == 0:
				i, j = 1, 1
				pass
			else:
				if self.clients[x][0] not in self.inside.keys():
					i += 1
					nowy = Button(text=f"{self.clients[x][0]}, {self.clients[x][1]}, {self.clients[x][2]}",
								  size_hint=(0.2, 0.1), pos_hint={'x': (0.2 * cx + 30) / cx,
																  'y': (cy - 100 * i - 15) / cy})
					nowy.bind(on_press=self.get_in)
					self.out_widgets.append(nowy)
				else:
					j += 1
					nowy = Button(text=f"{self.clients[x][0]}, {self.clients[x][1]}, {self.clients[x][2]}",
								  size_hint=(0.2, 0.1), pos_hint={'x': 10/cx,
																  'y': (cy - 100 * j - 15) / cy})
					nowy.bind(on_press=self.get_out)
					self.inside_widgets.append(nowy)
		for t in self.out_widgets:
			self.add_widget(t)
		for t in self.inside_widgets:
			self.add_widget(t)
		pass
	def get_csv(self):
		try:
			with open('in.csv', newline='') as csvfile:
				spam = csv.reader(csvfile, delimiter=',', quotechar='\n')
				for row in spam:
					self.inside[row[0]] = row[1]
		except IOError:
			with open('in.csv', 'w') as f:
				f.write("id,timestamp\n")
				f.write(f"0,{time.time()}\n")
				f.write(f"1,{time.time()-60*60*3}\n")
				f.write(f"2,{time.time()-60*60*1}\n")
			with open('in.csv', newline='') as csvfile:
				spam = csv.reader(csvfile, delimiter=',', quotechar='\n')
				for row in spam:
					self.inside[row[0]] = row[1]
		try:
			with open('clients.csv', newline='') as csvfile:
				spam = csv.reader(csvfile, delimiter=',', quotechar='\n')
				for row in spam:
					self.clients[row[0]] = row

		except IOError:
			with open('clients.csv', 'w') as f:
				f.write("id,imie,nazwisko,time_left\n")
				f.write(f"0,Mark,Suckerberg,{60*60*5}\n")
				f.write(f"1,Hanna,JOLO,{60*60*2}\n")
				f.write(f"2,Beata,Blitz,{60*60*4}\n")
			with open('clients.csv', newline='') as csvfile:
				spam = csv.reader(csvfile, delimiter=',', quotechar='\n')
				for row in spam:
					self.clients[row[0]] = row
		pass
	def get_out(self, widget):
		self.remove_widget(widget)
		index = widget.text.split(", ")[0]
		timestamp = self.inside[index]
		del self.inside[index]
		self.clients[index][3] = float(self.clients[index][3]) - (time.time()-float(timestamp))
		self.update_visuals()
		self.update_csv()
		pass
	def get_in(self, widget):
		index = widget.text.split(", ")[0]
		dane = self.clients[index]
		time_left = float(dane[3])
		if time_left <= 0:
			content = Button(text="Klient nie ma godzin na karnecie!\nProsze kupić godziny w okie obok!")
			popup = Popup(content=content, auto_dismiss=False, title='', size_hint=(0.5, 0.5))
			content.bind(on_press=popup.dismiss)
			popup.open()
		else:
			self.remove_widget(widget)
			self.inside[index] = time.time()
			self.update_visuals()
			self.update_csv()
	def update_visuals(self, whyyyyyyyyy="fu"):
		global cx, cy, Window
		cx, cy = Window.size
		self.clear_widgets()
		self.inside_widgets = []
		self.out_widgets = []
		self.display()
		self.drop.remove_widget(self.drop.select)
		self.drop.remove_widget(self.drop.hours)
		self.drop.remove_widget(self.drop.slider)

		self.remove_widget(self.screen)
		self.remove_widget(self.drop)

		del self.screen
		del self.drop

		self.screen = Screen()
		self.drop = Drop()
		self.drop.add_widget(self.dropdown)
		self.create_time_menu()
		self.add_widget(self.screen)
		self.add_widget(self.drop)

		self.dropdown.select("Wybierz klienta:")
		pass
	def update_csv(self):
		with open('in.csv', 'w') as f:
			for x in self.inside.keys():
				f.write(f"{x},{self.inside[x]}\n")
		with open('clients.csv', 'w') as f:
			for x in self.clients.keys():
				f.write(f"{x},{self.clients[x][1]},{self.clients[x][2]},{self.clients[x][3]}\n")
		pass
	def create_time_menu(self):
		self.drop.select.bind(on_release=self.dropdown.open)
		self.drop.hours.bind(on_press=self.buy_hours)
		self.dropdown.clear_widgets()
		for klucze in self.clients.keys():
			if klucze != 'id':
				option = Button(
					text=f"{self.clients[klucze][0]}, {self.clients[klucze][1]}, {self.clients[klucze][2]}, {str(round(int(float(self.clients[klucze][3])) / 60 / 24, 2))+'dni' if round(int(float(self.clients[klucze][3])) / 60 / 24, 2)>=1 else str(round(int(float(self.clients[klucze][3])) / 60, 2))+'godzin'}",
					size_hint_y=None, size_hint=(100, None), height=60)
				option.bind(on_release=lambda option: self.dropdown.select(option.text))
				self.dropdown.add_widget(option)
		self.dropdown.bind(on_select=lambda instance, x: setattr(self.drop.select, 'text', x))
		pass
	def buy_hours(self, why_does_it_always_send_back_the_bound_button_it_should_be_off_by_default):
		if self.drop.select.text != "Wybierz klienta:":
			dane = self.drop.select.text.split(", ")
			print(dane)
			try:
				dane[3] = str(float(dane[3][:-3])*24*60 + (float(self.drop.slider.value)*60))
			except ValueError:
				dane[3] = str(float(dane[3][:-6])*24 + (float(self.drop.slider.value)*60))
			self.clients[dane[0]] = dane
			self.update_csv()
			self.update_visuals()
		else:
			content = Button(text="Klient nie został wybrany!\nProszę wybrać klienta w okie obok!")
			popup = Popup(content=content, auto_dismiss=True, title='', size_hint=(0.5, 0.5))
			content.bind(on_press=popup.dismiss)
			popup.open()
	def add_new_guy(self, aghhhhhhhhhhhhhhh):
		print("ffff")
		content = FloatLayout()
		self.user = []
		self.new_client_popup = Popup(content=content, auto_dismiss=False, title='', size_hint=(1, 1))

		lab = Label(text = "Imie:", pos = (600, 800), size_hint=(0.1, 0.1))
		TI = TextInput(text="", pos = (800, 830), size_hint=(0.1, 0.05), multiline=False)
		lab2 = Label(text = "Nazwisko:", pos = (600, 650), size_hint=(0.1, 0.1))
		TI2 = TextInput(text="", pos = (800, 670), size_hint=(0.1, 0.05), multiline=False)
		butt = Button(text = "Anuluj/Wróć", pos = (600, 500), size_hint=(0.1, 0.1))
		butt2 = Button(text = "Dodaj", pos = (800, 500), size_hint=(0.1, 0.1))
		butt.bind(on_press=self.new_client_popup.dismiss)
		butt2.bind(on_press=self.add_new_guy_sub)

		content.add_widget(lab)
		content.add_widget(TI)
		content.add_widget(lab2)
		content.add_widget(TI2)
		content.add_widget(butt)
		content.add_widget(butt2)

		self.user.append(TI)
		self.user.append(TI2)

		self.new_client_popup.open()
		pass
	def add_new_guy_sub(self, aghhhhhhhhhhhhhhhhhhhhhhsdfdsfsd):
		temp = self.user
		print(temp)
		if temp[0] != '' or temp[1] != '':
			temp[0] = temp[0].text
			temp[1] = temp[1].text
			print(temp)
			index = max(list(self.clients.keys())[1:])
			index = str(int(index)+1)
			self.clients[index] = [index, temp[0], temp[1], float(31*24*60)]
		self.update_csv()
		self.update_visuals()
		self.new_client_popup.dismiss()
		pass

# class MyApp(App):
# 	@staticmethod
# 	def build():
# 		return Main()

if __name__ == '__main__':
	# MyApp().run()
	main = Main()
	runTouchApp(main)
	pass