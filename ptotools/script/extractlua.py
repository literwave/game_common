#!/usr/bin/env python
# -*- encoding:utf8 -*-

import sys, os, re
import shutil
from tracemalloc import start

COMMON_PTO_NAME = "common.proto"

class parseFile():

	def __init__(self, dir):
		self._dir = dir
		self._commonPtoName = COMMON_PTO_NAME
		self._reMessage = re.compile(r"message\s\w+")
		self._namePreFix = {"c2s", "s2c"}
		self.startParse()
		
	def isPtoFile(self, fileName):
		if fileName == self._commonPtoName:
			return False
		filetype = fileName[-6:]
		return (filetype == ".proto")
	
	def startParse(self):
		client_pto_dir = "../client/proto/pto/"
		if not os.path.exists(client_pto_dir):
			os.makedirs(client_pto_dir)

		print(os.listdir(self._dir))
		for fileName in os.listdir(self._dir):
			if fileName.endswith(".proto"):
				src_file = os.path.join(self._dir, fileName)
				dst_file = os.path.join(client_pto_dir, fileName)
				shutil.copy(src_file, dst_file)
				print(f"Copied {fileName} to {client_pto_dir}")

			if self.isPtoFile(fileName):
				with open(self._dir + fileName, encoding = "utf8") as f:
					ptoBuf = f.read()
					ptoNameList = self._reMessage.findall(ptoBuf)
					print(ptoNameList)
					for ptotoName in ptoNameList:
						ptoName = ptotoName.replace("message", "").strip()
						if not ptoName[0:3] in self._namePreFix:
							continue

if __name__ == "__main__":
	dir = "./" if len(sys.argv)<=1  else sys.argv[1]
	if not dir.endswith('/') and not dir.endswith('\\'):
		dir += '/'
	parseFile = parseFile(dir)