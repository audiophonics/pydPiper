#!/usr/bin/python
# coding: UTF-8

# Abstract Base class to provide display primitives
# Written by: Ron Ritchey
import math, abc, logging, time, imp
from PIL import Image
from PIL import ImageDraw

class widget:
	__metaclass__ = abc.ABCMeta

	def __init__(self, variabledict={ }):
		# width and height.  In pixels for graphics displays and characters for character displays
		self.width = 0						# Width of the widget
		self.height = 0						# Height of the widget
		self.size = (0,0)					# Size of the widget
		self.type = None					# What type of widget this is.  Used to determine what to do on a refresh.
		self.image = None					# A render of the current contents of the widget.
		self.variables = []					# Names of variables in to-be-used order
		self.currentvardict = { }			# A record of any variables that have been used and their last value
		self.variabledict = variabledict	# variabledict.  A pointer to the current active system variable db

	@abc.abstractmethod
	def update(self):
		# Refresh content based upon current variables
		return

	# Widgets
	@abc.abstractmethod
	def text(self, formatstring, fontpkg, variabledict={ }, variables =[], varwidth = False, size=(0,0), just=u'left'):
		# Input
		# 	msg (unicode) -- msg to display
		#	(w,h) (integer tuple) -- Bounds of the rectangle that message will be written into.  If set to 0, no restriction on size.
		#	fontpkg (font object) -- The font that the message should be rendered in.
		#	varwidth (bool) -- Whether the font should be shown monospaced or with variable pitch
		#	just (unicode) -- Determines how to justify the text horizontally.  Allowed values [ 'left','right','center' ]
		return

	@abc.abstractmethod
	def progressbar(self, value, rangeval, size, style=u'square',variabledict={ }):
		# Input
		#	value (numeric) -- Value of the variable showing progress.
		#	range (numeric tuple) -- Range of possible values.  Used to calculate percentage complete.
		#	size (number tuple) -- width and height to draw progress boundary
		#	style (unicode) -- Sets the style of the progress bar.  Allowed values [ 'rounded', 'square' ]
		return

	@abc.abstractmethod
	def line(self, (x,y), color=1):
		# Input
		#	(x,y) (integer  tuple) -- Draw line between origin and x,y.
		#	color (integer) -- color of the line
		return

	@abc.abstractmethod
	def rectangle(self, (x,y), fill=0, outline=1):
		# Input
		#	(x,y) (integer  tuple) -- Lower right of rectanble drawn from the origin
		#	color (integer) -- color of the rectangle
		return

	@abc.abstractmethod
	def canvas(self, (w,h)):
		# Input
		#	(w,h) (integer  tuple) -- size of canvas
		return

	@abc.abstractmethod
	def popup(self, widget, dheight, duration=15, pduration=10):
		# Input
		#	widget (widget) -- Widget to pop up
		#	dheight (integer) -- Sets the height of the window which will get displayed from the canvas
		#	duration (float) -- How long to display the top of the canvas
		#	pduration (float) -- How long to stay popped up
		return

	@abc.abstractmethod
	def scroll(self, widget, direction=u'left', distance=1, gap=20, hesitatetype=u'onloop', hesitatetime=2, threshold=0,reset=False):
		# Input
		#	widget (widget) -- Widget to scroll
		#	direction (unicode) -- What direction to scroll ['left', 'right','up','down']
		#	hesitatetype (unicode) -- the type of hesitation to use ['none', 'onstart', 'onloop']
		#	hesitatetime (float) -- how long in seconds to hesistate
		#	threshold (integer) -- scroll only if widget larger than threshold
		#	reset (bool) -- Should the hesitation timer be reset
		return

	# Utility functions
	def updatesize(self):
		if self.image != None:
			self.width = self.image.width
			self.height = self.image.height
			self.size = self.image.size
		else:
			self.width = 0
			self.height = 0
			self.size = (0,0)

	def transformvariable(self, val, name):
		# Implement transformation logic (e.g. |yesno, |onoff |upper |bigchars+0)
		# Format of 'name' is the name of the transform preceded by a '|' and
		# then if variables are required a series of values seperated by '+' symbols


		transforms = name.split(u'|')
		if len(transforms) == 0:
			return ''
		elif len(transforms) == 1:
			return val

		retval = val
		# Compute transforms
		for i in range(1,len(transforms)):
			transform_request = transforms[i].split(u'+')[0] # Pull request type away from variables
			if transform_request in [u'onoff',u'truefalse',u'yesno']:
				# Make sure input is a Boolean
				if type(val) is bool:

					if transform_request == u'onoff':
						retval = u'on' if val else u'off'
					elif transform_request == u'truefalse':
						retval = u'true' if val else u'false'
					elif transform_request == u'yesno':
						retval = u'yes' if val else u'no'
				else:
					logging.debug(u"Request to perform boolean transform on {0} requires boolean input").format(name)
					return val
			elif transform_request in [u'upper',u'capitalize',u'title',u'lower']:
				# These all require string input

				if type(val) is str or type(val) is unicode:
					if type(retval) is str:
						retval = retval.decode()
					if transform_request == u'upper':
						retval = retval.upper()
					elif transform_request == u'capitalize':
						retval = retval.capitalize()
					elif transform_request == u'title':
						retval = retval.title()
					elif transform_request == u'lower':
						retval = retval.lower()
				else:
					logging.debug(u"Request to perform transform on {0} requires string input").format(name)
					return val
			elif transform_request in [ u'bigchars',u'bigplay' ]:
				# requires a string input
				# bigchars requires a variable to specify which line of the msg to return


				tvalues = transforms[i].split('+')[1:]

				if len(tvalues) > 2:
					# Safe to ignore but logging
					logging.debug(u"Expected at most two but received {0} variables".format(len(values)))

				if len(tvalues) == 0:
					# Requires at least one variable to specify line so will return error in retval
					logging.debug(u"Expected one but received no variables")
					retval = u"Err"
				else:

					if transform_request == u'bigchars':
						try:
							if len(tvalues) == 2: # Request to add spaces between characters
								es = u"{0:<{1}}".format('',int(tvalues[1]))
								val = es.join(val)

							retval = displays.fonts.size5x8.bigchars.generate(val)[int(tvalues[0])]
						except (IndexError, ValueError):
							logging.debug(u"Bad value or line provided for bigchar")
							retval = u'Err'
					elif transform_request == u'bigplay':
						try:
							if len(tvalues) == 2: # Request to add spaces between characters
								es = u"{0:<{1}}".format('',int(tvalues[1]))
								val = es.join(val)

							retval = displays.fonts.size5x8.bigplay.generate(u'symbol')[int(tvalues[0])] + '  ' + displays.fonts.size5x8.bigplay.generate(u'page')[int(tvalues[0])]
						except (IndexError, ValueError):
							logging.debug(u"Bad value or line provided for bigplay")
							retval = u'Err'

		return retval

	def clear(self,image,x,y,width,height):
		draw = ImageDraw.Draw(image)
		draw.rectangle((x,y, x+width-1, y+height-1),0)

	def evaltext(self, formatstring, variables):
		# return a string that places variables according to formatstring instructions

		parms = []
		try:
			for k in range(len(variables)):
				varname = variables[k].split(u'|')[0]
				val = self.transformvariable(self.variabledict[varname], variables[k])
				parms.append(val)
		except KeyError:
			logging.debug( u"Variable not found in evaltext.  Values requested are {0}".format(variables) )
			# Format doesn't match available variables
			segval = u"VarErr"
			return segval

		# create segment to display
		try:
			segval = formatstring.format(*parms)
		except:
			logging.debug( u"Var Error Format {0}, Parms {1} Vars {2}".format(format, parms, vars) )
			# Format doesn't match available variables
			logging.debug(u"Var Error with parm type {0} and format type {1}".format(type(parms), type(format)))
			segval = u"VarErr"

		return segval

	def changed(self, variables):
		# variables (unicode array) -- An array containing the names of the variables being used
		# returns bool based upon whether any variables that have been used have changed since the last time a render was requested
		for v in variables:
			try:
				if self.variabledict[v] != self.currentvardict[v]:
					return True
			except KeyError:
				return True
		return False


class gwidget(widget):

	def update(self, reset=False):

		if self.type in ['text', 'progressbar']:
			if not self.changed(self.variables):
				return False

		if self.type == 'text':
			self.text(self.formatstring, self.variables, self.fontpkg, self.varwidth, self.size, self.just)
			return True
		elif self.type == 'progressbar':
			self.progressbar(self.value, self.rangeval, self.size, self.style)
			return True
		elif self.type == 'canvas':
			retval = True if reset else False
			for e in self.widgets:
				widget,x,y,w,h = e
				if widget.update(reset):
					retval = True
			# If a widget has changed
			if retval:
				# Clear canvas
				self.clear()
				# Replace all of the widgets
				for e in self.widgets:
					widget,x,y,w,h = e
					self.place(widget, (x,y), (w,h))
			return retval
		elif self.type == u'scroll':
			return self.scroll(self.widget, self.direction, self.distance, self.gap, self.hesitatetype, self.hesitatetime,self.threshold, reset)
		elif self.type == u'popup':
			return self.popup(self.widget, self.dheight, self.duration, self.pduration)
		else:
			return False

	# WIDGETS

	# CANVAS widget functions
	def canvas(self, (w,h)):
		self.type = u'canvas'
		self.image = Image.new("1", (w,h) )
		self.updatesize()

	def add(self, widget, (x,y), (w,h)=(0,0)): # Add a widget to the canvas

		if self.type != u'canvas':
			logging.warning("Trying to add a widget to something that is not a canvas")
			return

		try:
			self.widgets
		except:
			# initialize widgets array
			self.widgets = []

		self.widgets.append( (widget,x,y,w,h) )
		self.place(widget, (x,y), (w,h) )
		return self

	def clear(self): # Erase canvas
		if self.type != u'canvas':
			logging.warning('Trying to clear a widget that is not a canvas')
			return
		self.image = Image.new("1", (self.image.width, self.image.height))

	def place(self, widget, (x,y), size=(0,0)): # Place a widget's image on the canvas
		# Input
		#	widget (widget): widget to place
		#	(x,y) (integer tuple): where to place it
		#	size (integer tuple): how big should it be
		if self.type != u'canvas':
			logging.warning(u"Trying to place a widget on something that is not a canvas")
			return

		w,h = size
		if w > 0 or h > 0:
			img = widget.image.crop( (0,0,0+w,0+h) )
		else:
			img = widget.image

		self.image.paste(img, (x,y))

	# TEXT widget functions
	def textsize(self, msg, fontpkg, varwidth): # returns the size needed to contain provided message
		# Input
		#	msg (unicode): string that contains the message for the calculation
		#	fontpkg (fontpkg): the font to use for the calculation
		#	varwidth (bool): Should the font be fixed or variable width

		maxw = 0
		maxh = 0
		cx = 0
		(fx,fy) = fontpkg['size']

		for c in msg:

			if c == u'\n':
				maxh = maxh + fy
				if cx > maxw:
					maxw = cx
				cx = 0
				continue

			try:
				charimg = fontpkg[ord(c)]
			except KeyError:
				# Requested character does not exist in font.  Replace with '?'
				charimg = fontpkg[ord('?')]

			if varwidth:
				cx += charimg.width
			else:
				cx += fx

		if cx > maxw:
			maxw = cx
		maxh = maxh + fy

		return ((maxw, maxh))

	def text(self, formatstring, variables, fontpkg, varwidth = False, size=(0,0), just=u'left'):
		# Input
		# 	formatstring (unicode) -- format string
		#	variables (unicode array) -- list of variables used to populate formatstring.  Variable values come from variabledict.
		#	fontpkg (font object) -- The font that the message should be rendered in.
		#	varwidth (bool) -- Whether the font should be shown monospaced or with variable pitch
		#	size (integer tuple) -- Size of image if larger than text size
		#	just (unicode) -- Determines how to justify the text horizontally.  Allowed values [ 'left','right','center' ]

		# Save variables used for this text widget
		self.currentvardict = { }
		for v in variables:
			self.currentvardict[v] = self.variabledict[v]

		# size parameters for future updates
		self.type = u'text'
		self.formatstring = formatstring
		self.variables = variables
		self.fontpkg = fontpkg
		self.varwidth = varwidth
		self.just = just

		(fx,fy) = fontpkg['size']
		cx = 0
		cy = 0
		cw = 0

		msg = self.evaltext(formatstring, variables)

		# initialize image

		maxw, maxh = self.textsize(msg, fontpkg, varwidth)

		# msglines = msg.split('\n')
		# maxw = 0
		# for line in msglines:
		# 	if maxw < len(line):
		# 		maxw = len(line)
		# maxw = maxw * fx
		# maxh = len(msglines) * fy

		# If a size was provided that is larger than what is required to display the text
		# expand the image size as appropriate
		width, height = size
		maxw = maxw if maxw > width else width
		maxh = maxh if maxh > height else height
		self.image = Image.new("1", (maxw, maxh), 0)

		lineimage = Image.new("1", (maxw, fy), 0)
		for c in msg:

			# If newline, move y to next line (based upon font height) and return x to beginning of line
			if c == u'\n':
				# Place line into image
				if just == u'left':
					ax = 0
				elif just == u'center':
					ax = (maxw-cx)/2
				elif just == u'right':
					ax = (maxw-cx)
				self.image.paste(lineimage, (ax, cy))
				lineimage = Image.new("1", (maxw, fy), 0)
				cy = cy + fy
				cx = 0
				continue

			try:
				charimg = fontpkg[ord(c)]
			except KeyError:
				# Requested character does not exist in font.  Replace with '?'
				charimg = fontpkg[ord('?')]


			# Adjust charimg if varwidth is False
			if not varwidth:
				offset = (fx-charimg.width)/2
				charimg = charimg.crop( (-offset,0,fx-offset,fy) )
				charimg.load()

			# Paste character into frame
			lineimage.paste(charimg, (cx,0))

			# Erase space between characters
			draw = ImageDraw.Draw(lineimage)
			draw.rectangle((cx+charimg.width,0, cx+charimg.width, fy-1),0)

			# Move to next character position
			if varwidth:
				cx += charimg.width
			else:
				cx += fx

		# # resize to exact requirement of message
		# self.image.crop((0,0,cx-1, cy+fy))

		# Place last line into image
		if just == u'left':
			ax = 0
		elif just == u'center':
			ax = (maxw-cx)/2
		elif just == u'right':
			ax = (maxw-cx)
		self.image.paste(lineimage, (ax, cy))

		self.updatesize()

		return self.image

	# def image(self, file,(h,w)=(0,0)):
	# 	# Input
	# 	#	file (unicode) -- filename of file to retrieve image from.  Must be located within the images directory.
	# 	#	(h,w) (integer tuple) -- Bounds of the rectangle that image will be written into.  If set to 0, no restriction on size.
	# 	return

	# PROGRESSBAR widget function
	def progressbar(self, value, rangeval, size, style=u'square'):
		# Input
		#	value (numeric) -- Value of the variable showing progress.
		#	rangeval (numeric tuple) -- Range of possible values.  Used to calculate percentage complete.
		#	size (number tuple) -- width and height to draw progress bar
		#	style (unicode) -- Sets the style of the progress bar.  Allowed values [ 'rounded', 'square' ]

		self.variables = []

		# Convert variable to value if needed
		if type(value) is unicode:
			v = self.variabledict[value] if value in self.variabledict else 0
			if value in self.variabledict:
				self.variables.append(value)
		elif type(value) is int or type(value) is float:
			v = value
		else:
			v = 0

		l,h = rangeval
		# Convert range low to value if needed
		if type(l) is unicode:
			rvlow = self.variabledict[l] if l in self.variabledict else 0
			if l in self.variabledict:
				self.variables.append(l)
		elif type(l) is int or type(l) is float:
			rvlow = l
		else:
			rvlow = 0

		# Convert range high to value if needed
		if type(h) is unicode:
			rvhigh = self.variabledict[h] if h in self.variabledict else 0
			if h in self.variabledict:
				self.variables.append(h)
		elif type(h) is int or type(h) is float:
			rvhigh = h
		else:
			rvhigh = 0

		# Save variables used for this progressbar widget
		self.currentvardict = { }
		for sv in self.variables:
			self.currentvardict[sv] = self.variabledict[sv]

		width, height = size

		# correct values if needed
		if rvhigh < rvlow:
			t = rvlow
			rvlow = rvhigh
			rvhigh = t

		if v < rvlow or v > rvhigh:
			raise ValueError

		percent = (v - rvlow) / float((rvhigh - rvlow))

		# make image to place progress bar
		self.image = Image.new("1", size, 0)

		if style == u'square':
			draw = ImageDraw.Draw(self.image)
			draw.line( (0,0,0,height-1),1)
			for i in range (0,int((width-2)*percent)):
				draw.line( (i+1,0,i+1,height-1),1)
			for i in range (int((width-2)*percent), width-2):
				self.image.putpixel((i+1,0), 1)
				self.image.putpixel((i+1,height-1), 1)
			draw.line( (width-1,0,width-1,height-1),1)

		self.updatesize()

		# Save parameters for update
		self.value = value
		self.rangeval = rangeval
		self.style = style
		self.type = 'progressbar'

		return self.image

	# LINE widget function
	def line(self, (x,y), color=1):
		# Input
		#	(x,y) (integer tuple) -- Draw a line from the origin to x,y
		#	color -- color to use for the line

		# Does image exist yet?
		if self.image == None:
			self.image = Image.new("1", (x+1, y+1), 0)
		else:
			# Is image big enough?
			if self.image.width < x or self.image.height < y:
				self.image.crop(0,0,x,y)

		draw = ImageDraw.Draw(self.image)
		draw.line( (0,0,x,y) ,color)

		self.updatesize()

		# save parameters
		self.xy = (x,y)
		self.color = color

		return self.image

	# RECTANGLE widget function
	def rectangle(self, (x,y), fill=0, outline=1):
		# Input
		#	(x,y) (integer tuple) -- Bottom left and bottom right of rectangle drawn from origin
		#	color -- color to use for the rectangle

		# Does image exist yet?
		if self.image == None:
			self.image = Image.new("1", (x+1, y+1), 0)
		else:
			# Is image big enough?
			if self.image.width < x or self.image.height < y:
				self.image.crop(0,0,x,y)

		draw = ImageDraw.Draw(self.image)
		draw.rectangle((0,0,x,y),fill, outline)

		self.updatesize()

		# save parameters
		self.xy = (x,y)
		self.fill = fill
		self.outline = outline

		return self.image

	# POPUP widget function
	def popup(self, widget, dheight, duration=15, pduration=10): # Set up for pop-up display
		# Input
		#	widget (widget) -- Widget to pop up
		#	dheight (integer) -- Sets the height of the window which will get displayed from the canvas
		#	duration (float) -- How long to display the top of the canvas
		#	pduration (float) -- How long to stay popped up

		# If this is the first pass, initialize state variables
		try:
			self.popped
		except:
			self.type = u'popup'
			self.popped = False
			self.end = time.time() + duration
			self.image = widget.image
			self.updatesize()
			self.index = 0

			# Save parameters
			self.widget = widget
			self.dheight = dheight
			self.duration = duration
			self.pduration = pduration

		# Update the widget if needed
		self.widget.update()

		# If we are waiting for a transition
		if self.end > time.time():
			self.image = self.widget.image.crop( (0, self.index, self.widget.width-1, self.index+self.dheight) )
			self.updatesize()
			return True

		if self.popped:
			# Move back into non-popped mode
			if self.index > 0:
				self.index -= 1
			else:
				self.popped = False
				self.end = time.time()+self.duration
		else:
			# Move into popped mode
			if self.index < self.widget.height - self.dheight:
				self.index += 1
			else:
				self.popped = True
				self.end = time.time() + self.pduration

		self.image = self.widget.image.crop( (0, self.index, self.widget.width-1, self.index+self.dheight) )
		self.updatesize()

		return True

	# SCROLL widget function
	def scroll(self, widget, direction=u'left', distance=1, gap=20, hesitatetype=u'onloop', hesitatetime=2, threshold=0, reset=False): # Set up for scrolling
		# Input
		#	widget (widget) -- Widget to scroll
		#	direction (unicode) -- What direction to scroll ['left', 'right','up','down']
		#	hesitatetype (unicode) -- the type of hesitation to use ['none', 'onstart', 'onloop']
		#	hesitatetime (float) -- how long in seconds to hesistate
		#	threshold (integer) -- scroll only if widget larger than threshold

		retval = False
		if reset:
			self.start = time.time()
			if hesitatetype not in ['onstart', 'onloop']:
				self.end = 0
			else:
				self.end = self.start + hesitatetime

		# If this is the first pass, initialize state variables
		try:
			self.type
			self.end
		except:
			retval = True
			self.type= u'scroll'
			self.start = time.time()
			if hesitatetype not in ['onstart', 'onloop']:
				self.end = 0
			else:
				self.end = self.start + hesitatetime
			self.image = widget.image.copy()
			self.index = 0
			self.updatesize()

			self.shouldscroll = False

			# Save parameters
			self.widget = widget
			direction = direction.lower()
			self.direction = direction
			self.distance = distance
			self.gap = gap
			hesitatetype = hesitatetype.lower()
			self.hesitatetype = hesitatetype
			self.hesitatetime = hesitatetime
			self.threshold = threshold

			# Check to see if scrolling is needed
			if self.direction in ['left','right']:
				if self.widget.width > self.threshold:
					self.shouldscroll = True
				else:
					self.shouldscroll = False
			elif self.direction in ['up','down']:
				if self.widget.height > self.threshold:
					self.shouldscroll = True
				else:
					self.shouldscroll = False

			# Expand canvas
			if self.shouldscroll:
				if direction in ['left','right']:
					self.image = Image.new("1", (self.widget.width+gap, self.widget.height))
					self.image.paste(self.widget.image, (0,0))
					self.updatesize()
				elif direction in ['up','down']:
					self.image = Image.new("1", (self.widget.width, self.widget.height+gap))
					self.image.paste(self.widget.image, (0,0))
					self.updatesize()


		if self.widget.update(reset):
			# something has changed
			retval = True
			self.start = time.time()
			if hesitatetype not in ['onstart', 'onloop']:
				self.end = 0
			else:
				self.end = self.start + hesitatetime
			self.image = self.widget.image.copy()
			self.index = 0
			self.updatesize()

			# Check to see if scrolling is needed
			if self.direction in ['left','right']:
				if self.widget.width > self.threshold:
					self.shouldscroll = True
				else:
					self.shouldscroll = False
			elif self.direction in ['up','down']:
				if self.widget.height > self.threshold:
					self.shouldscroll = True
				else:
					self.shouldscroll = False

			if self.shouldscroll:
				# Expand canvas
				if direction in ['left','right']:
					self.image = Image.new("1", (self.widget.width+gap, self.widget.height))
					self.image.paste(self.widget.image, (0,0))
					self.updatesize()
				elif direction in ['up','down']:
					self.image = Image.new("1", (self.widget.width, self.widget.height+gap))
					self.image.paste(self.widget.image, (0,0))
					self.updatesize()

		# If Hesitate is needed or scrolling is not needed, return
		if self.end > time.time() or not self.shouldscroll:
			return retval

		# Save region to be overwritten
		# Move body
		# Restore region to cleared space

		image = self.image
		width = self.width
		height = self.height

		if direction == u'left':
			region = image.crop((0,0, distance, height))
			body = image.crop((distance,0, width, height))
			image.paste(body, (0,0))
			image.paste(region, ((width-distance),0) )
			if hesitatetype == u'onloop':
				self.index += distance
				if self.index >= width:
					self.index = 0
					self.start = time.time()
					self.end = self.start + hesitatetime
		elif direction == u'right':
			region = image.crop((width-distance,0, width, height))
			body = image.crop((0,0, width-distance, height))
			image.paste(body, (distance,0) )
			image.paste(region, (0,0) )
			if hesitatetype == u'onloop':
				self.index += distance
				if self.index >= width:
					self.index = 0
					self.start = time.time()
					self.end = self.start + hesitatetime
		elif direction == u'up':
			region = image.crop((0,0, width, distance))
			body = image.crop((0,distance, width, height))
			image.paste(body, (0,0) )
			image.paste(region, (0,height-distance) )
			if hesitatetype == u'onloop':
				self.index += distance
				if self.index >= height:
					self.index = 0
					self.start = time.time()
					self.end = self.start + hesitatetime
		elif direction == u'down':
			region = image.crop((0,height-distance, width, height))
			body = image.crop((0,0, width, height-distance))
			image.paste(body, (0,distance) )
			image.paste(region, (0,0) )
			if hesitatetype == u'onloop':
				self.index += distance
				if self.index >= height:
					self.index = 0
					self.start = time.time()
					self.end = self.start + hesitatetime

		return True

class gwidgetText(gwidget):
	def __init__(self, formatstring, fontpkg, variabledict={ }, variables =[], varwidth = False, size=(0,0), just=u'left'):
		super(gwidgetText, self).__init__(variabledict)
		self.text(formatstring, variables, fontpkg, varwidth, size, just)

class gwidgetProgressBar(gwidget):
	def __init__(self, value, rangeval, size, style=u'square',variabledict={ }):
		super(gwidgetProgressBar, self).__init__(variabledict)
		self.progressbar(value, rangeval, size, style)

class gwidgetLine(gwidget):
	def __init__(self, (x,y), color=1):
		super(gwidgetLine, self).__init__()
		self.line((x,y), color)

class gwidgetRectangle(gwidget):
	def __init__(self, (x,y), fill=0, outline=1):
		super(gwidgetRectangle, self).__init__()
		self.rectangle((x,y), fill, outline)

class gwidgetCanvas(gwidget):
	def __init__(self, (w,h)):
		super(gwidgetCanvas, self).__init__()
		self.canvas((w,h))

class gwidgetPopup(gwidget):
	def __init__(self, widget, dheight, duration=15, pduration=10):
		super(gwidgetPopup, self).__init__()
		self.popup(widget, dheight, duration, pduration)

class gwidgetScroll(gwidget):
	def __init__(self, widget, direction=u'left', distance=1, gap=20, hesitatetype=u'onloop', hesitatetime=2, threshold=0, reset=False):
		super(gwidgetScroll, self).__init__()
		self.scroll(widget, direction, distance, gap, hesitatetype, hesitatetime,threshold,reset)


class sequence(object): # Holds a sequence of widgets to display on the screen in turn
	def __init__(self, conditional, db, dbprevious, coolingperiod): # initialize class
		# Input
		#	conditional (unicode) -- a string containing an evaluable boolean logic statement which determines whether the sequence is active
		#	db (dict) -- A dictionary that points to system variable db
		#	dbp (dict) -- A dictionary that points to the previous state of the system variable db
		#	coolingperiod (float) -- Amount of time to wait before a sequence can be displayed again

		self.widgets = []					# Array to hold widget list
		self.conditional = conditional		# Sequence conditional.  Must be true for sequence to be displayed
		self.db = db						# System variable db
		self.dbp = dbprevious				# System variable db for previous values (to allow system to detect changes)
		self.coolingperiod = coolingperiod	# Wait for coolingperiod seconds before allowing this sequence to be displayed again
		self.coolingexpires = 0				# Variable to mark the time that the sequence exits its coolingperiod
		self.end = 0						# Variable to mark the time that the current widget expires
		self.currentwidget = 0				# Marks the index of the current widget
		return

	def add(self, widget, duration, conditional): # Add a widget to the display sequence
		# Input
		#	widget (widget) -- The widget to add to the display seqeunce
		#	duration (float) -- How long in seconds to display this widget
		#	conditional (unicode) -- A string containing an evaluable boolean logic statement which determines whether the widget should be included in the sequence
		self.widgets.append( (widget, duration, conditional) )

	def evalconditional(self, conditional): # Evaluate the conditional statement
		# Input
		#	conditional (unicode) -- A string containing an evaluable boolean logic statement

		# This is NOT a safe routine.  Make sure that any input sent to this function is from a trusted source

		db = self.db
		dbp = self.dbp

		try:
			return eval(conditional)
		except:
			# Could not evaluate conditional so returning False
			return False

 	def get(self, restart=False): # Return current widget (or None) if none are active
		# Input
		#	restart (bool) -- If True resets the sequence to the first widget on the list

		# Evaluate sequence conditional and check for cooling period.
		if not self.evalconditional(self.conditional) or self.coolingexpires > time.time():
			return None

		widget, duration, conditional = self.widgets[self.currentwidget]

		# Check and respond to restart
		if restart:
			self.currentwidget = 0
			self.coolingexpires = 0
			widget, duration, conditional = self.widgets[self.currentwidget]
			self.end = duration + time.time()

		# See if current widget has expired (or has gone inactive).
		if self.end < time.time() or not self.evalconditional(conditional):
			# If it has, iterate through list to find the next active widget
			self.currentwidget += 1
			if self.currentwidget >= len(self.widgets):
				self.currentwidget = 0

			for i in range(len(self.widgets)):
				widget, duration, conditional = self.widgets[self.currentwidget]
				if self.evalconditional(conditional):
					self.end = duration + time.time()
					widget.update(True)
					return widget
				else:
					self.currentwidget += 1
					if self.currentwidget >= len(self.widgets):
						self.currentwidget = 0


			# If you go through the whole list without finding an active widget then return None
			return None
		else:
			# If current widget is active and has not expired, then return it
			widget.update()
			return widget

class display_controller(object):
	def __init__(self, file, db, dbp):
		self.file = file
		self.db = db
		self.dbp = dbp
		self.load(file)

	def load(self, file): # Load config file and initialize sequences
		# Input
		#	file (unicode) -- file that contains a valid display configuration

		self.pages = None
		self.widgets = { }
		self.sequences = []

		logging.debug("Loading {0} as page file".format(file))
		# If page file provided, try to load provided file on top of default pages file
		try:
			newpages = imp.load_source('pages', file)
				# Need to have the following structures to be valid
			self.pages = newpages
		except:
			logging.critical('Page file {0} was unable to be loaded'.format(file))
			self.pages = None

		# Load fonts
		for k,v in self.pages.FONTS.iteritems():
			fontfile = v['file'] if 'file' in v else ''
			if fontfile:
				try:
					v['fontpkg'] = fonts.bmfont.bmfont(fontfile).fontpkg
				except:
					# Font load failed
					logging.critical('Attempt to load font {0} failed'.format(fontfile))
			else:
				logging.critical('Expected a font file for {0} but none provided'.format(k))


		# Add type field to CANVAS widgets
		for k,v in self.pages.CANVASES.iteritems():
			v['type'] = 'canvas'

		self.loadwidgets(self.pages.WIDGETS)
		self.loadwidgets(self.pages.CANVASES)
		self.loadsequences(self.pages.SEQUENCES)




	def loadwidgets(self, pageWidgets): # Load widgets. Return any widgets that could not be loaded because a widget contained within it was not found

		# Load widgets
		for k,v in pageWidgets.iteritems():
			typeval = v['type'].lower() if 'type' in v else ''

			if typeval not in ['canvas', 'text', 'progressbar', 'line', 'rectangle' ]:
				if typeval:
					logging.warning('Attempted to add widget {0} with an unsupported widget type {1}.  Skipping...'.format(k,typeval))
				else:
					logging.warning('Attempted to add widget {0} without a type specified.  Skipping...'.format(k))
				continue

			# type if valid
			if typeval == 'text':
				format = v['format'] if 'format' in v else ''
				variables = v['variables'] if 'variables' in v else []
				font = v['font'] if 'font' in v else ''
				just = v['just'] if 'just' in v else 'left'
				size = v['size'] if 'size' in v else (0,0)
				varwidth = v['varwidth'] if 'varwidth' in v else False
				fontentry = self.pages.FONTS[font] if font in self.pages.FONTS else None
				fontpkg = fontentry['fontpkg'] if 'fontpkg' in fontentry else None
				if not format or not fontpkg:
					logging.warning('Attempted to add text widget {0} without a format or font specified.  Skipping...'.format(k))
					continue
				widget = gwidgetText(format, fontpkg, self.db, variables, varwidth, size, just)
			elif typeval == 'progressbar':
				value = v['value'] if 'value' in v else None
				rangeval = v['rangeval'] if 'rangeval' in v else (0,100)
				size = v['size'] if 'size' in v else None
				style = v['style'] if 'style' in v else 'square'
				if not value or not size:
					logging.warning('Attempted to add progressbar widget {0} without a value or size.  Skipping...'.format(k))
					continue
				widget = gwidgetProgressBar(value, rangeval, size, style, self.db)
			elif typeval == 'line':
				point = v['point'] if 'point' in v else None
				color = v['color'] if 'color' in v else 1
				if not point:
					logging.warning('Attempted to add line widget {0} without a point.  Skipping...'.format(k))
					continue
				widget = gwidgetLine(point, color)
			elif typeval == 'rectangle':
				point = v['point'] if 'point' in v else None
				fill = v['fill'] if 'fill' in v else 0
				outline = v['outline'] if 'outline' in v else 1
				if not point:
					logging.warning('Attempted to add rectangle widget {0} without a point.  Skipping...'.format(k))
					continue
				widget = gwidgetRectangle(point, fill, outline)
			elif typeval == 'canvas':
				widgetentries = v['widgets'] if 'widgets' in v else []
				size = v['size'] if 'size' in v else None

				if not size:
					logging.warning('Attempted to add create canvas {0} without a size.  Skipping...'.format(k))
					continue

				widget = gwidgetCanvas(size)
				for wtuple in widgetentries:
					try:
						 wname, x, y = wtuple
					except ValueError:
						logging.warning('Canvas {0} included widget that does not have the appropriate number of parameters. Skipping widget...'.format(k))
						continue
					if type(x) is not int or type(y) is not int:
						logging.warning('Canvas {0} included a widget with an invalid point to place the widget. Skipping widget...'.format(k))
						continue

					widtoadd = self.widgets[wname] if wname in self.widgets else None
					if not widtoadd:
						logging.warning('Canvas {0} attempted to add widget {1} but it was not found in the widget list'.format(k, wname))
						continue

					widget.add(widtoadd, (x,y))

			# Add effect if requested
			effect = v['effect'] if 'effect' in v else None
			if effect != None:
				try:
					etype = effect[0]
				except IndexError:
					etype = ''
				if etype in ['scroll', 'popup']:
					if etype == 'scroll':
						widget = gwidgetScroll(widget, *effect[1:])
					elif etype == 'popup':
						widget = gwidgetPopup(widget, *effect[1:])
				else:
					if etype:
						logging.warning('Attempted to add an unrecognized effect ({0}) to widget {1}.  Ignoring...'.format(etype,k))
					else:
						logging.warning('Attempted to an effect to widget {0} without specifying the details.  Ignoring...'.format(k))

			# Add widget to widget list
			self.widgets[k] = widget
			print "Adding widget {0}".format(k)

	def next(self): # Compute and return the next image to display
		active = []
		for s in self.sequences:
			w = s.get()
			if w != None:
				active.append(w)
				# If sequence does not have an active coolingperiod timer set then set one
				if s.coolingexpires < time.time():
					s.coolingexpires = s.coolingperiod + time.time()
		img = None
		for w in active:
			if not img:
				img = w.image
			else:
				# If more than one sequence is active, paste together.
				w = w.image.width if w.image.width > img.width else img.width
				h = w.image.height if w.image.height > img.height else img.height
				if w > img.width or h > img.height:
					img = img.crop(0,0,w,h)
				img.paste(w.image,(0,0))
		return img

	def loadsequences(self, sequences):

		for k,v in sequences.iteritems():
			conditional = v['conditional'] if 'conditional' in v else 'False'
			coolingperiod = v['coolingperiod'] if 'coolingperiod' in v else 0
			newseq = sequence(conditional,self.db,self.dbp, coolingperiod)
			self.sequences.append(newseq)
			canvases = v['canvases'] if 'canvases' in v else []
			if canvases:
				for c in canvases:
					name = c['name'] if 'name' in c else ''
					duration = c['duration'] if 'duration' in c else 0
					conditional = c['conditional'] if 'conditional' in c else 'False'
					if name and duration and conditional:
						widget = self.widgets[name] if name in self.widgets else None
						if widget:
							newseq.add(widget,duration, conditional)
						else:
							logging.warning('Trying to add widget {0} to sequence {1} but widget was not found'.format(name, k))

			# If no canvases were added to the sequence, remove it
			if len(newseq.widgets) == 0:
				logging.warning('Unable to create sequence {0}.  No widgets'.format(k))
				del self.sequences[-1]


def printsequences(seq):
	for s in seq:
		print "SEQUENCE"
		print '  Canvases      : {0}'.format(len(s.widgets))
		print '  Conditional   : {0}'.format(s.conditional)
		print '  Cooling Period: {0}'.format(s.coolingperiod)


if __name__ == '__main__':

	import graphics as g
	import fonts

	starttime = time.time()
	elapsed = int(time.time()-starttime)
	timepos = time.strftime(u"%-M:%S", time.gmtime(int(elapsed))) + "/" + time.strftime(u"%-M:%S", time.gmtime(int(254)))

	db = {
	 		'title':"When dove's cry",
			'artist':"Prince and the Revolutions",
			'album':'Purple Rain',
			'playlist_display':'01/10',
			'elapsed_formatted':timepos,
			'time_formatted':'12:34p',
			'outside_temp_formatted':'72\xb0F',
			'outside_conditions':'Windy',
			'volume':88,
			'system_temp_formatted':'98\xb0C',
			'streaming':False,
			'state':'play',
			'random':False,
			'single':False,
			'repeat':False,
			'system_tempc':98.0
		}


	dbp = {
	 		'title':"When dove's cry",
			'artist':"Prince and the Revolutions",
			'album':'Purple Rain',
			'playlist_display':'01/10',
			'elapsed_formatted':'1:32/4:03',
			'time_formatted':'12:34p',
			'outside_temp_formatted':'72\xb0F',
			'outside_conditions':'Windy',
			'volume':88,
			'system_temp_formatted':'98\xb0C',
			'streaming':False,
			'state':'play',
			'random':False,
			'single':False,
			'repeat':False,
			'system_tempc':98.0
		}

	dc = display_controller('../pages.py', db,dbp)
	printsequences(dc.sequences)

	# titlew = dc.widgets['title']

	# formatstring, fontpkg, variabledict={ }, variables =[], varwidth = False, size=(0,0), just=u'left'

	fontpkg = dc.pages.FONTS['small']['fontpkg']
	# fontpkg = fonts.bmfont.bmfont(u'latin1_5x8.fnt').fontpkg
	elapsedw = gwidgetText("{0}", fontpkg, db, [u'elapsed_formatted'], False, (60,8), 'right')
	artistw = gwidgetText("{0}", fontpkg, db, [u'album'], False )
	playlist_displayw = gwidgetText("{0}", fontpkg, db, [u'playlist_display'], False )
	canvasw = gwidgetCanvas( (100,16) )
	canvasw.add(artistw, (0,0) )
	canvasw.add(playlist_displayw, (0,8))
	canvasw.add(elapsedw, (40,8))

	frame = g.getframe( canvasw.image, 0,0,canvasw.image.width,canvasw.image.height)
	g.show( frame, canvasw.image.width, int(math.ceil(canvasw.image.height/8.0)) )


	starttime = time.time()
	elapsed = int(time.time()-starttime)
	timepos = time.strftime(u"%-M:%S", time.gmtime(int(elapsed))) + "/" + time.strftime(u"%-M:%S", time.gmtime(int(254)))

	time.sleep(2)
	while True:
		elapsed = int(time.time()-starttime)
		timepos = time.strftime(u"%-M:%S", time.gmtime(int(elapsed))) + "/" + time.strftime(u"%-M:%S", time.gmtime(int(254)))
		db['elapsed_formatted'] = timepos
		img = dc.next()
		frame = g.getframe( img, 0,0, 100,16 )
		g.show( frame, 100, int(math.ceil(16/8.0)))
		time.sleep(.1)

# 	variabledict = { u'artist':u'Prince and the Revolutions', u'title':u'Million Dollar Club', u'volume':50 }
# 	variables = [ u'artist', u'title' ]
#
# 	f_HD44780 = fonts.bmfont.bmfont(u'latin1_5x8.fnt')
# 	fp_HD44780 = f_HD44780.fontpkg
#
# 	fp_Vint10x16 = fonts.bmfont.bmfont(u'Vintl01_10x16.fnt').fontpkg
#
# 	# artistw = gwidget(u'artist', variabledict)
# 	# artistw.text(u"{0}",[u'artist'], fp_Vint10x16, True, (0,0), 'left')
#
# 	artistw = gwidgetText("{0}",fp_Vint10x16, variabledict, [u'artist'], True)
# 	titlew = gwidgetText("{0}", fp_HD44780, variabledict, [u'title'], True)
# 	linew = gwidgetLine( (99,0) )
# 	rectw = gwidgetRectangle( (99,15) )
# 	progw = gwidgetProgressBar(u'volume', (0,100), (80,6), u'square', variabledict)
#
# 	artistcanvas = gwidgetCanvas( (artistw.width,14) )
# 	titlecanvas = gwidgetCanvas( (artistw.width,8) )
#
# 	# artistcanvas = gwidgetScroll(artistcanvas.add( artistw, (0,0) ),u'left')
# 	# titlecanvas = gwidgetScroll(titlecanvas.add( titlew, (0,0) ),u'up')
# 	artistcanvas = gwidgetScroll(artistw,u'left',1,20,u'onloop',2,100)
# 	titlecanvas = gwidgetScroll(titlew,u'left',1,4,u'onloop',2,100)
#
# 	page = gwidgetCanvas( (100,32) )
# 	page.add(artistcanvas, (0,0))
# 	page.add(titlecanvas, (0,14), (100,8))
# 	page.add(linew, (0,22))
# 	page.add(progw, (4,24))
#
# 	end = time.time() + 20
# 	flag = True
# 	i = 0
# 	variabledict['volume'] = i
# 	while end > time.time():
# 		i += 1
# 		if i > 100:
# 			i = 0
# 		variabledict['volume'] = i
# 		if end < time.time()+10 and flag:
# 			variabledict['title'] = u"Purple Rain"
# 			flag = False
# 		if page.update():
# 			frame = g.getframe( page.image, 0,0, page.width, page.height)
# 			g.show( frame, page.width, int(math.ceil(page.height/8.0)))
# 			time.sleep(.03)
#
# #-------------
#
# 	variabledict['title'] = "When Dove's Cry"
# 	progw = gwidgetProgressBar(u'volume', (0,100), (80,4), u'square', variabledict)
# 	page = gwidgetCanvas( (100,32) )
# 	page.add( artistcanvas, (0,0) )
# 	page.add( titlecanvas, (0,18) )
# 	page.add( linew, (0,26) )
# 	page.add( progw, (0,28) )
# 	page = gwidgetPopup(page, 14)
#
# 	end = time.time() + 25
# 	flag = True
# 	i = 0
# 	variabledict['volume'] = i
# 	while end > time.time():
# 		i += 1
# 		if i > 100:
# 			i = 0
# 		variabledict['volume'] = i
# 		if end < time.time()+15 and flag:
# 			variabledict['title'] = u"Purple Rain"
# 			flag = False
# 		if page.update():
# 			frame = g.getframe( page.image, 0,0, page.width, page.height)
# 			g.show( frame, page.width, int(math.ceil(page.height/8.0)))
# 		time.sleep(.03)