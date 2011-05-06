# -*- coding: utf-8 -*-

from exceptions import BufferNotFound
from liborgmode import Document
import vim

class VimBuffer(Document):
	def __init__(self, bufnr=0):
		"""
		:bufnr:		0: current buffer, every other number refers to another buffer
		"""
		Document.__init__(self)
		self._bufnr = bufnr

	@property
	def bufnr(self):
		"""
		:returns:	The buffer's number for the current document
		"""
		return self._bufnr

	def load(self):
		if self._bufnr == 0:
			self._content = vim.current.buffer
		else:
			_buffer = None
			for b in vim.buffers:
				if self._bufnr == b.number:
					_buffer = b
					break

			if not _buffer:
				raise BufferNotFound('Unable to locate buffer number #%d' % self._bufnr)
			self._content = _buffer
		return Document.load(self)

	def write(self):
		""" write the changes to the vim buffer

		:returns:	True if something was written, otherwise False
	    """
		if not self.is_dirty:
			return False

		# write meta information
		if self.is_dirty_meta_information:
			meta_end = 0 if self._orig_meta_information_len == None else self._orig_meta_information_len
			self._content[:meta_end] = self._meta_information
			self._orig_meta_information_len = len(self._meta_information)
			self._dirty_meta_information = False

		# remove deleted headings
		already_deleted = []
		for h in sorted(self._deleted_headings, cmp=lambda x, y: cmp(x._orig_start, y._orig_start), reverse=True):
			if h._orig_start != None and h not in already_deleted:
				# this is a heading that actually exists on the buffer and it
				# needs to be removed
				del self._content[h._orig_start:h._orig_start + h._orig_len]
				already_deleted.append(h)
		del self._deleted_headings[:]
		del already_deleted

		# update changed headings and add new headings
		for h in self.all_headings():
			if h.is_dirty:
				if h._orig_start != None:
					# this is a heading that existed before and was changed. It
					# needs to be replaced
					if h.is_dirty_heading:
						self._content[h.start:h.start + 1] = [str(h)]
					if h.is_dirty_body:
						self._content[h.start + 1:h.start + h._orig_len] = h.body
				else:
					# this is a new heading. It needs to be inserted
					self._content[h.start:h.start] = [str(h)] + h.body
				h._dirty_heading = False
				h._dirty_body = False
			# for all headings the length and start offset needs to be updated
			h._orig_start = h.start
			h._orig_len = len(h)

		self._dirty = False
		return True

	def previous_heading(self):
		""" Find the next heading (search forward) and return the related object
		:returns:	 Heading object or None
		"""
		h = self.current_heading()
		if h:
			return h.previous_heading

	def current_heading(self):
		""" Find the current heading (search backward) and return the related object
		:returns:	Heading object or None
		"""
		position = vim.current.window.cursor[0] - 1
		for h in self.all_headings():
			if h.start <= position and h.end >= position:
				return h

	def next_heading(self):
		""" Find the next heading (search forward) and return the related object
		:returns:	 Heading object or None
		"""
		h = self.current_heading()
		if h:
			return h.next_heading
