#!/usr/bin/python
# -*- coding: UTF-8 -*-
from __future__ import print_function
import os
import xlrd
import xlwt
import sys
import time
import re
import traceback

keyInfo = 'L2Lo, SentDataMeasurementCounting.hpp'	#used to filter the syslog
#the original output info in the log
rawInfoInLogLine1=('ttisFromUpdate', 'numOfBearers', 'nrCellId', 'TBS', 'MacCe', 'StatusPdu', 'DataPdu', 'Rcvd', 'Sent', 'Buffered')
rawInfoInLogLine2=('nrCellId', 'iniTxPktsRcvd', 'reTxPktsRcvd', 'usedBuffers', 'allocated', 'released')
# the title in the target xls file
# here add time, deltaRcvd and deltaSent
title=('day', 'time', 'ttisFromUpdate', 'numOfBearers', 'nrCellId', 'TBS', 'MacCe', 'StatusPdu', 'DataPdu', 'Rcvd', 'deltaRcvd', 'Sent', 'deltaSent', 'Buffered', 'iniTxPktsRcvd', 'reTxPktsRcvd', 'usedBuffers', 'allocated', 'released')

cellId2Rcvd = {'CellId':0}
cellId2Sent = {'CellId':0}
pre_line1Data = {'CellId': range(len(title))}
sheets = {}
rowOfCellId = {}

def CreateSheetOfCellId(cellId):
	print("### add sheet for cellId:", cellId)
	sheet_ceId = book.add_sheet(str(cellId), cell_overwrite_ok=True)
	sheets[cellId] = sheet_ceId
	for index in range(len(title)):
		sheets[cellId].write(0, 0 + index, title[index])
	rowOfCellId[cellId] = 1
	
	#add _Mbps data
	index += 1
	sIndex = title.index('TBS')
	for i in range(0, 9):
		sheets[cellId].write(0, i + index, title[sIndex + i] + '_Mbps')
	
	#add column title tsFlag for time line
	sheets[cellId].write(0, 1 + i + index, 'tsFlag')
	
def addLinedataToSheetOfCell(rdata):
	cellId = rdata[title.index('nrCellId')]
	tmp_row = rowOfCellId[cellId]
	tmp_col = 0
	for i in range(0, len(rdata)):
		sheets[cellId].write(tmp_row, tmp_col, rdata[i])
		tmp_col += 1
	rowOfCellId[cellId] += 1
	
	#add data of unit Mbps
	sIndex = title.index('TBS')
	for i in range(0, 9):
		v_Mbps = round(rdata[sIndex + i] * 8 / 1024 / 1024, 2)
		sheets[cellId].write(tmp_row, tmp_col, v_Mbps)
		tmp_col += 1
	
	sheets[cellId].write(tmp_row, tmp_col, 0)
	
def parseLine1(line, row, col):
	tempData = [0, 0]
	#get time
	timeList = pattern1.findall(line)
	ss = timeList[-1][1:-2].split('T')
	tempData[0] = ss[0]
	tempData[1] = ss[1].split('.')[0]
	#get nrCellId and so on
	subLine = line[line.index(rawInfoInLogLine1[0]): -1]
	data_res = pattern.findall(subLine)
	for i in range(0, len(rawInfoInLogLine1)):
		tempData.append(int(data_res[i]))

	#calculate for deltaRcvd and deltaSent
	index_Rcvd = title.index('Rcvd')
	index_sent = title.index('Sent')
	cellId = tempData[title.index('nrCellId')]
	global cellId2Rcvd
	global cellId2Sent
	if cellId in cellId2Rcvd:
		deltaRcvd = tempData[index_Rcvd] - cellId2Rcvd[cellId]
		tempData.insert(index_Rcvd+1, deltaRcvd)
		deltaSent = tempData[index_sent] - cellId2Sent[cellId]
		tempData.insert(index_sent+1, deltaSent)
	else:
		CreateSheetOfCellId(cellId)
		cellId2Rcvd[cellId] = 0
		cellId2Sent[cellId] = 0
		tempData.insert(index_Rcvd+1, 0)
		tempData.insert(index_sent+1, 0)

	cellId2Rcvd[cellId] = tempData[index_Rcvd]
	cellId2Sent[cellId] = tempData[index_sent]
	
	global pre_line1Data
	if len(tempData) !=  4 + len(rawInfoInLogLine1):
		print ('#### Error happen in the line:', line, '\n#### tempData:', tempData)
		exit(-1)
	pre_line1Data[cellId] = tempData
	
def parseLine2(line, row, col):
	tempData = [0, 0]
	#get time
	timeList = pattern1.findall(line)
	ss = timeList[-1][1:-2].split('T')
	tempData[0] = ss[0]
	tempData[1] = ss[1].split('.')[0]
	
	#get nrCellId and so on
	subLine = line[line.index(rawInfoInLogLine2[0]): -1]
	data_res = pattern.findall(subLine)
	for i in range(0, len(rawInfoInLogLine2)):
		tempData.append(int(data_res[i]))
	time2 = tempData[1]
	cellId = tempData[2]
	
	global pre_line1Data
	if not cellId in pre_line1Data:
		return False
	
	line1data = pre_line1Data[cellId]
	del pre_line1Data[cellId] #clear the list of key cellId
	time1 = line1data[1]
	if time1 != time2:
		print ('#### Error for line:', line, '\n#### time mismatch for cellId:', cellId, ' line1 time:', time1, 'line2 time:', time2)
		return False
	
	for i in range(3, len(tempData)):
		line1data.append(tempData[i])
	
	for j in range(0, len(line1data)):
		sheet.write(row, col, line1data[j])
		col += 1
		#print("CellID:", line1data[4], "\n", line1data)
		#os._exit(0)
	#also add the line data to it's cellId's sheet
	addLinedataToSheetOfCell(line1data)
	return True
	
############### start ##############

if len(sys.argv) != 2:
    print('Error:Please add filename after the script!')
    exit(-1)
inputFileName = sys.argv[1]
if not os.path.exists(inputFileName):
    print ('Error: File', inputFileName, 'not exist!')
    exit(-1)

inputFileName = sys.argv[1]

#inputFileName = 'SYSLOG_755.LOG'
#1. create a workbook
book = xlwt.Workbook(encoding='utf-8',style_compression=0)

# 2. create a sheet, name it as 'dataMeasurement'
sheet = book.add_sheet('dataMeasurement', cell_overwrite_ok=True)

# 3. add the title to the sheet
row = 0; col = 0
for index in range(len(title)):
	sheet.write(row, col + index, title[index])

# 4. parse log
row = 1; col = 0
pattern = re.compile(r'\d+')   # find all the number
pattern1 = re.compile(r'<\d+-\d+-\w+:\d+:\d+.\w+>') #used to find the time
with open(inputFileName,'r') as raw:
	for line in raw.readlines():
		if not line.__contains__(keyInfo):
			continue
		line = line.strip('\n')
		try:
			if line.__contains__("ttisFromUpdate"):
				#handle for line1
				parseLine1(line, row, col)
			else:
				#handle for line2
				if parseLine2(line, row, col):
					row += 1; col = 0
			
		except ValueError as e:
			print ("##### Error! The line content is wrong:", line)
			traceback.print_exc()
		except IndexError as e:
			traceback.print_exc()
			print (line)
			exit(-1)
		#row += 1; col = 0

# 5. save the result to xls file in the same folder of the log.
print ("### inputFileName is:", inputFileName)
# switch to the directory of the log
if inputFileName.find('\\') > 0:
    outDirPath = inputFileName[0:inputFileName.rindex('\\')]
    os.chdir(outDirPath)
    OutputFileName = inputFileName[inputFileName.rindex('\\') + 1:inputFileName.rindex('.')]
else:
    OutputFileName = inputFileName[:inputFileName.rindex('.')]

print ("### OutputFileName is:", OutputFileName)
# replace the special characters to '.' and then split it
#OutputFileName = re.sub(r"[\/\\\:\*\?\"\<\>\|]",'.',inputFileName).split('.')[:-2]

# if the output file exist, remove the output file
if(os.path.exists(OutputFileName+'.xls')):
    os.remove(OutputFileName+'.xls')
book.save(OutputFileName+'.xls')

print ('Parse L2LO measurement data successfully! See the result in', os.getcwd()+'\\'+OutputFileName+'.xls')

