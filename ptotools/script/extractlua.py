#!/usr/bin/env python
# -*- encoding:utf8 -*-

from genericpath import exists
import sys, os, re
import shutil
from tracemalloc import start
import slpp
import json

COMMON_PTO_NAME = "common.proto"
START_PTO_BASE_ID = 256
MAX_PTO_ID = 65535
ID_TO_NAME = {}

PREFIX = "table = "
def _NewLine(count):
    return '\n' + '    ' * count

def _ToLua(out, obj, indent=1):
    if isinstance(obj, int) or isinstance(obj, float):
       out.append(json.dumps(obj, ensure_ascii = False))
    elif(isinstance(obj, str)):
        if obj.find(PREFIX) == 0:
            out.append(obj[len(PREFIX):])
        else:
            out.append(json.dumps(obj, ensure_ascii = False))
    else:
        isList = isinstance(obj, list)
        out.append('{')
        isFirst = True
        for i in obj:
            if isFirst:
                isFirst = False
            else:
                out.append(',')
            out.append(_NewLine(indent))
            if not isList:
                # obj[i] 
                k = i
                i = obj[k]
                # out.append('[')
                if isinstance(k, int) or isinstance(k, float):
                    out.append(str(k))
                else:
                #     out.append('"')
                    out.append(str(k))
                #     out.append('"')
                # out.append(']')
                out.append(' = ')
            _ToLua(out, i, indent + 1)
        out.append(_NewLine(indent - 1))
        out.append('}')

def execute_lua_str():
    return '''\
\nID_TO_PACK_NAME = {}
PTONAME_TO_ID = {}
PACK_NAME_TO_ID = {}
ID_TO_PTONAME = {} -- 这里需要优化，其实就只有客户端发给后端才需要这个数据
for_maker = {}
for_caller = {}
	
local function initPto()
	for mod, packTbl in pairs(define) do
		for ptoName, id in pairs(packTbl) do
			local packName = mod .. "." .. ptoName
			ID_TO_PACK_NAME[id] = packName
			PTONAME_TO_ID[ptoName] = id
			PACK_NAME_TO_ID[packName] = id
			ID_TO_PTONAME[id] = ptoName
		end
	end
end

initPto()
'''

class parseFile():

	def __init__(self, dir):
		self._idToMod = {}
		self._nameToId = {}
		self._dumpNameId = {}
		self._dir = dir
		self._startId = START_PTO_BASE_ID
		self._commonPtoName = COMMON_PTO_NAME
		self._reWrite = False
		self._reMessage = re.compile(r"message\s\w+")
		self._rePack = re.compile(r"(package)(\s\w+)")
		self._namePreFix = {"c2s", "s2c"}
		self.startParse()
		self.dumpFile()
		
	def isPtoFile(self, fileName):
		if fileName == self._commonPtoName:
			return False
		filetype = fileName[-6:]
		return (filetype == ".proto")
	
	def startParse(self):
		# 这里用json做中间逻辑其实是为了方法好调用
		# 需要支持全部重新导出
		json_path = "../client/proto/netPb.json"
		if exists(json_path):
			with open(json_path, "r+", encoding = "utf8") as f:
				ptoBuf = f.read()
				pto = json.loads(ptoBuf)
				difine = pto.get("define")
				if difine:
					for k, v in difine.items():
						for kk, vv in v.items():
							self._nameToId[kk] = vv
							self._idToMod[vv] = k
							# After loading all existing IDs, set startId to max ID + 1
							if self._nameToId:
								self._startId = max(self._nameToId.values()) + 1
		
		# 确保目标目录存在
		client_pto_dir = "../client/proto/pto/"
		if not os.path.exists(client_pto_dir):
			os.makedirs(client_pto_dir)

		found_protos = set()
		print(os.listdir(self._dir))
		for fileName in os.listdir(self._dir):
			if fileName.endswith(".proto"):
				# 复制文件到 client/proto/pto
				src_file = os.path.join(self._dir, fileName)
				dst_file = os.path.join(client_pto_dir, fileName)
				shutil.copy(src_file, dst_file)
				print(f"Copied {fileName} to {client_pto_dir}")

			if self.isPtoFile(fileName):
				with open(self._dir + fileName, encoding = "utf8") as f:
					ptoBuf = f.read()
					modName = self._rePack.findall(ptoBuf)
					ptoModName = modName[0][1].strip()
					ptoNameList = self._reMessage.findall(ptoBuf)
					print(ptoNameList)
					for ptotoName in ptoNameList:
						ptoName = ptotoName.replace("message", "").strip()
						if not ptoName[0:3] in self._namePreFix:
							print(f"error,ptoName: {ptoName}")
							raise ValueError
						
						found_protos.add(ptoName)

						# 看是否在旧的协议中
						if ptoName in self._nameToId:
							# 检查包名是否变化
							old_id = self._nameToId[ptoName]
							if self._idToMod.get(old_id) != ptoModName:
								print(f"Update package for {ptoName}: {self._idToMod.get(old_id)} -> {ptoModName}")
								self._idToMod[old_id] = ptoModName
								self._reWrite = True
							continue
						
						self._startId
						if self._startId >= MAX_PTO_ID:
							print(f"error, _startId: {self._startId}, please extend")
						print(self._startId, ptoModName, ptoName)
						self._nameToId.update({ptoName: self._startId})
						self._idToMod.update({self._startId: ptoModName})
						self._startId += 1
						self._reWrite = True

		# 清理不存在的旧协议
		all_names = list(self._nameToId.keys())
		for name in all_names:
			if name not in found_protos:
				print(f"Remove old protocol: {name}")
				old_id = self._nameToId[name]
				del self._nameToId[name]
				if old_id in self._idToMod:
					del self._idToMod[old_id]
				self._reWrite = True

	def dumpFile(self):
		# 构建 define 字典，即使没有新协议也要生成文件
		define = self._dumpNameId.get("define")
		if not define:
			define = self._dumpNameId["define"] = {}
		for ptotoName, ptoId in self._nameToId.items():
			ptoModName = self._idToMod[ptoId]
			if not define.get(ptoModName):
				define[ptoModName] = {}
			define[ptoModName][ptotoName] = ptoId
		
		# 如果有新协议，更新 JSON 文件
		if self._reWrite:
			print(self._dumpNameId)
			tem = json.dumps(self._dumpNameId, indent=True)
			# wirte json
			with open("../client/proto/netPb.json", "w", encoding = "utf8") as f:
				f.write(tem)
		
		# 总是生成 lua 文件（即使没有新协议）
		luaDataTbl = []
		_ToLua(luaDataTbl, define)
		luaStr = "local define = "
		luaStr = luaStr + "".join(luaDataTbl) + execute_lua_str()
		with open("../server/proto/netPb.lua", "w", encoding = "utf8") as f:
			f.write(luaStr)

if __name__ == "__main__":
	dir = "./" if len(sys.argv)<=1  else sys.argv[1]
	if not dir.endswith('/') and not dir.endswith('\\'):
		dir += '/'
	parseFile = parseFile(dir)