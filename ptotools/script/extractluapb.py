#!/usr/bin/env python
# -*- encoding:utf8 -*-

from genericpath import exists
import sys, os, re
from tracemalloc import start
import slpp
import json


def get_protoc_path(script_dir):
	# 优先查找本地的 protoc.exe
	paths_to_check = [
		os.path.join(script_dir, '../bin/protoc.exe'),
		os.path.join(script_dir, '../protoc.exe'),
	]
	for path in paths_to_check:
		if os.path.exists(path):
			return os.path.abspath(path)
	return "protoc" # 默认使用环境变量中的 protoc

def main(dir):
	script_dir = os.path.dirname(os.path.abspath(__file__))
	protoc_exe = get_protoc_path(script_dir)
	print(f"Using protoc: {protoc_exe}")

	# 确保目录路径正确
	if not dir.endswith('/') and not dir.endswith('\\'):
		dir += '/'
	
	out_lua_dir = os.path.join(dir, '../../../server/proto/pb/')
	out_cs_dir = os.path.join(dir, '../outcs/')

	if not os.path.exists(out_lua_dir):
		os.makedirs(out_lua_dir)
	if not os.path.exists(out_cs_dir):
		os.makedirs(out_cs_dir)

	for filename in os.listdir(dir):
		if filename.endswith(".proto"):
			print(f"Processing: {filename}")
			full_proto_path = os.path.join(dir, filename)
			
			# 生成 .pb 文件 (Lua使用)
			out_pb_path = os.path.join(out_lua_dir, filename[:-6] + ".pb")
			# Windows cmd bug: if command starts with quote, it might strip them. Wrap in extra quotes.
			cmd_pb = f'""{protoc_exe}" -o "{out_pb_path}" "{full_proto_path}" -I="{dir}""'
			print(cmd_pb)
			if os.system(cmd_pb) != 0:
				print(f"Failed to generate pb for {filename}")

			# 生成 C# 文件
			cmd_cs = f'""{protoc_exe}" "{full_proto_path}" --csharp_out="{out_cs_dir}" -I="{dir}""'
			print(cmd_cs)
			if os.system(cmd_cs) != 0:
				print(f"Failed to generate cs for {filename}")

if __name__ == "__main__":
	dir = "./" if len(sys.argv)<=1  else sys.argv[1]
	main(dir)

