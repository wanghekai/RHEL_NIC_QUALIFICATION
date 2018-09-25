import argparse
import csv
import glob
import os
import re
import sys
import tarfile
import xlsxwriter

DPDK_L3_PVP_PNGS = ['root/pvp_results_10_l3_dpdk/test_p2v2p_all_l3_ref.png',
                    'root/pvp_results_10_l3_dpdk/test_p2v2p_all_l3.png',
                    'root/pvp_results_10_l3_dpdk/test_p2v2p_1000000_l3.png',
                    'root/pvp_results_10_l3_dpdk/test_p2v2p_100000_l3.png',
                    'root/pvp_results_10_l3_dpdk/test_p2v2p_10000_l3.png',
                    'root/pvp_results_10_l3_dpdk/test_p2v2p_1000_l3.png',
                    'root/pvp_results_10_l3_dpdk/test_p2v2p_10_l3.png',]

DPDK_L2_PVP_PNGS = ['root/pvp_results_10_l2_dpdk/test_p2v2p_all_l2_ref.png',
                    'root/pvp_results_10_l2_dpdk/test_p2v2p_all_l2.png',
                    'root/pvp_results_10_l2_dpdk/test_p2v2p_1000000_l2.png',
                    'root/pvp_results_10_l2_dpdk/test_p2v2p_100000_l2.png',
                    'root/pvp_results_10_l2_dpdk/test_p2v2p_10000_l2.png',
                    'root/pvp_results_10_l2_dpdk/test_p2v2p_1000_l2.png',
                    'root/pvp_results_10_l2_dpdk/test_p2v2p_10_l2.png',]

KERNEL_L3_PVP_PNGS = ['root/pvp_results_10_l3_kernel/test_p2v2p_all_l3_ref.png',
                      'root/pvp_results_10_l3_kernel/test_p2v2p_all_l3.png',
                      'root/pvp_results_10_l3_kernel/test_p2v2p_1000000_l3.png',
                      'root/pvp_results_10_l3_kernel/test_p2v2p_100000_l3.png',
                      'root/pvp_results_10_l3_kernel/test_p2v2p_10000_l3.png',
                      'root/pvp_results_10_l3_kernel/test_p2v2p_1000_l3.png',
                      'root/pvp_results_10_l3_kernel/test_p2v2p_10_l3.png',]

KERNEL_L2_PVP_PNGS = ['root/pvp_results_10_l2_kernel/test_p2v2p_all_l2_ref.png',
                      'root/pvp_results_10_l2_kernel/test_p2v2p_all_l2.png',
                      'root/pvp_results_10_l2_kernel/test_p2v2p_1000000_l2.png',
                      'root/pvp_results_10_l2_kernel/test_p2v2p_100000_l2.png',
                      'root/pvp_results_10_l2_kernel/test_p2v2p_10000_l2.png',
                      'root/pvp_results_10_l2_kernel/test_p2v2p_1000_l2.png',
                      'root/pvp_results_10_l2_kernel/test_p2v2p_10_l2.png',]

TC_L3_PVP_PNGS = ['root/pvp_results_10_l3_tc/test_p2v2p_all_l3_ref.png',
                  'root/pvp_results_10_l3_tc/test_p2v2p_all_l3.png',
                  'root/pvp_results_10_l3_tc/test_p2v2p_1000000_l3.png',
                  'root/pvp_results_10_l3_tc/test_p2v2p_100000_l3.png',
                  'root/pvp_results_10_l3_tc/test_p2v2p_10000_l3.png',
                  'root/pvp_results_10_l3_tc/test_p2v2p_1000_l3.png',
                  'root/pvp_results_10_l3_tc/test_p2v2p_10_l3.png',]

TC_L2_PVP_PNGS = ['root/pvp_results_10_l2_tc/test_p2v2p_all_l2_ref.png',
                  'root/pvp_results_10_l2_tc/test_p2v2p_all_l2.png',
                  'root/pvp_results_10_l2_tc/test_p2v2p_1000000_l2.png',
                  'root/pvp_results_10_l2_tc/test_p2v2p_100000_l2.png',
                  'root/pvp_results_10_l2_tc/test_p2v2p_10000_l2.png',
                  'root/pvp_results_10_l2_tc/test_p2v2p_1000_l2.png',
                  'root/pvp_results_10_l2_tc/test_p2v2p_10_l2.png',]



class ResultsSheet(object):
    def __init__(self, args):
        """
        Constructor
        :param args: arguments parse object from command line output
        """
        self._args = args
        self._workbook = xlsxwriter.Workbook(self._args.output)
        self.client_file = args.client_tar_file
        self.server_file = args.server_tar_file
        self.pvp_dpdk_l2_ws = self._workbook.add_worksheet(
            'pvp_dpdk_l2_results')
        self.pvp_dpdk_l3_ws = self._workbook.add_worksheet(
            'pvp_dpdk_l3_results')
        self.pvp_kernel_l2_ws = self._workbook.add_worksheet(
            'pvp_kernel_l2_results')
        self.pvp_kernel_l3_ws = self._workbook.add_worksheet(
            'pvp_kernel_l3_results')
        self.vsperf_ws = self._workbook.add_worksheet(
            'throughput results')
        self.functional_ws = self._workbook.add_worksheet(
            'functional results')
        self.row = 0

    def close_workbook(self):
        """
        Close the workbook
        :return: None
        """
        self._workbook.close()

    def process_functional_results(self):
        """
        Process functional test results
        :return: None
        """
        # Open the tar files from the arguments
        tar1 = tarfile.open(self.client_file, "r")
        tar2 = tarfile.open(self.server_file, "r")
        self.functional_ws.set_column(0, 4, 30)

        def process_log(tar, member, column):
            """
            Process the log
            :param tar: tar file
            :param member: member inside tar file to process
            :param column: column to write to
            :return: Boolean if any test was a failure
            """
            self.row = 1
            column = column
            fh1 = tar.extractfile(member)
            data = fh1.readlines()
            fail_test = False
            for line in data:
                if "RESULT" in line:
                    findresult = re.search('\[   (PASS|FAIL)   \] :: RESULT: (\S+)', line)
                    if findresult.group(1) == 'FAIL':
                        fail_test = True
                    if findresult:
                        self.functional_ws.write_string(self.row, column, findresult.group(2))
                        self.functional_ws.write_string(self.row, column + 1, findresult.group(1))
                        self.row += 1
            return fail_test

        failed_results = list()
        for member in tar1.getnames():
            if 'client.log' in member:
                self.functional_ws.write_string(0, 0, 'Client results')
                failed_results.append(process_log(tar1, member, 0))
        for member in tar2.getnames():
            if 'server.log' in member:
                self.functional_ws.write_string(0, 2, 'Server results')
                failed_results.append(process_log(tar2, member, 2))

        if any(failed_results):
            self.functional_ws.name = self.functional_ws.name + ' (FAIL)'
        else:
            self.functional_ws.name = self.functional_ws.name + ' (PASS)'

    def process_pvp_results(self):
        """
        Process Eelcos pvp results
        :return: None
        """
        # get the pvp result files
        pvp_files = glob.glob('./pvp*.tgz')
        for result_file in pvp_files:
            tar = tarfile.open(result_file, "r:gz")
            # find the dpdk result file and process it
            if 'dpdk' in result_file:
                if self.write_pvp_worksheet(tar, 'root/pvp_results_1_l2_dpdk/test_results_l2.csv',
                                            self.pvp_dpdk_l2_ws, DPDK_L2_PVP_PNGS):
                    self.pvp_dpdk_l2_ws.name = self.pvp_dpdk_l2_ws.name + ' (FAIL)'
                else:
                    self.pvp_dpdk_l2_ws.name = self.pvp_dpdk_l2_ws.name + ' (PASS)'
                if self.write_pvp_worksheet(tar, 'root/pvp_results_1_l3_dpdk/test_results_l3.csv',
                                            self.pvp_dpdk_l3_ws, DPDK_L3_PVP_PNGS):
                    self.pvp_dpdk_l3_ws.name = self.pvp_dpdk_l3_ws.name + ' (FAIL)'
                else:
                    self.pvp_dpdk_l3_ws.name = self.pvp_dpdk_l3_ws.name + ' (PASS)'
            # find the kernel result file and process it
            elif 'kernel' in result_file:
                if self.write_pvp_worksheet(tar, 'root/pvp_results_1_l2_kernel/test_results_l2.csv',
                                            self.pvp_kernel_l2_ws, KERNEL_L2_PVP_PNGS):
                    self.pvp_kernel_l2_ws.name = self.pvp_kernel_l2_ws.name + ' (FAIL)'
                else:
                    self.pvp_kernel_l2_ws.name = self.pvp_kernel_l2_ws.name + ' (PASS)'
                if self.write_pvp_worksheet(tar, 'root/pvp_results_1_l3_kernel/test_results_l3.csv',
                                            self.pvp_kernel_l3_ws, KERNEL_L3_PVP_PNGS):
                    self.pvp_kernel_l3_ws.name = self.pvp_kernel_l3_ws.name + ' (FAIL)'
                else:
                    self.pvp_kernel_l3_ws.name = self.pvp_kernel_l3_ws.name + ' (PASS)'
            # find the tc_flower result file and process it
            elif 'tc' in result_file:
                #
                # Add TC flower results only if data is available as they are
                # optional.
                #
                self.pvp_tc_l2_ws = self._workbook.add_worksheet(
                    'pvp_tc_flower_l2_results')
                self.pvp_tc_l3_ws = self._workbook.add_worksheet(
                    'pvp_tc_flower_l3_results')
                self.pvp_tc_troughput_ws = self._workbook.add_worksheet(
                    'PVP TC Flower Throughput')

                if self.write_pvp_worksheet(tar, 'root/pvp_results_1_l2_tc/test_results_l2.csv',
                                            self.pvp_tc_l2_ws, TC_L2_PVP_PNGS):
                    self.pvp_tc_l2_ws.name = self.pvp_tc_l2_ws.name + ' (FAIL)'
                else:
                    self.pvp_tc_l2_ws.name = self.pvp_tc_l2_ws.name + ' (PASS)'
                if self.write_pvp_worksheet(tar, 'root/pvp_results_1_l3_tc/test_results_l3.csv',
                                            self.pvp_tc_l3_ws, TC_L3_PVP_PNGS):
                    self.pvp_tc_l3_ws.name = self.pvp_tc_l3_ws.name + ' (FAIL)'
                else:
                    self.pvp_tc_l3_ws.name = self.pvp_tc_l3_ws.name + ' (PASS)'
                if self.write_tc_throughput_worksheet(
                        tar,
                        'root/pvp_results_10_l3_tc/test_results_l3.csv'):
                    self.pvp_tc_troughput_ws.name = \
                        self.pvp_tc_troughput_ws.name + ' (FAIL)'
                else:
                    self.pvp_tc_troughput_ws.name = \
                        self.pvp_tc_troughput_ws.name + ' (PASS)'

    def process_throughput_results(self):
        """
        Process the vsperf results
        :return: None
        """
        self.vsperf_ws.set_column(0, 2, 30)

        bold_format = self._workbook.add_format()
        bold_format.set_bold()

        # setup column headers and passing result column
        self.vsperf_ws.write_string(0, 0, 'Test name', bold_format)
        self.vsperf_ws.write_string(0, 1, 'Test result', bold_format)
        self.vsperf_ws.write_string(0, 2, 'Required to pass', bold_format)
        self.vsperf_ws.write_string(1, 2, '3000000')
        self.vsperf_ws.write_string(2, 2, '1500000')
        self.vsperf_ws.write_string(3, 2, '6000000')
        self.vsperf_ws.write_string(4, 2, '1500000')
        self.vsperf_ws.write_string(5, 2, '1100000')
        self.vsperf_ws.write_string(6, 2, '250000')
        self.vsperf_ws.write_string(7, 2, '100000')
        self.vsperf_ws.write_string(8, 2, '100000')
        self.vsperf_ws.write_string(9, 2, '10000000')
        self.vsperf_ws.write_string(10, 2, '1500000')

        tar = tarfile.open(self.client_file, "r")
        test_fail = list()
        for member in tar.getnames():
            # find the vsperf result file
            if 'vsperf_result' in member:
                fh1 = tar.extractfile(member)
                data = fh1.readlines()

                for line in data:
                    if "64   Byte 2PMD OVS/DPDK PVP test result" in line:
                        self.vsperf_ws.write_string(1, 0, '64 Byte 2PMD 1Q DPDK', bold_format)
                        test_fail.append(self.write_throughput_pass_fail(
                            1, 1, str(int(float(line.split()[8]))), 3000000))
                    elif "1500 Byte 2PMD OVS/DPDK PVP test result" in line:
                        self.vsperf_ws.write_string(2, 0, '1500 Byte 2PMD 1Q DPDK', bold_format)
                        test_fail.append(self.write_throughput_pass_fail(
                            2, 1, str(int(float(line.split()[8]))), 1500000))
                    elif "64   Byte 4PMD 2Q OVS/DPDK PVP test result" in line:
                        self.vsperf_ws.write_string(3, 0, '64 Byte 4PMD 2Q DPDK', bold_format)
                        test_fail.append(self.write_throughput_pass_fail(
                            3, 1, str(int(float(line.split()[9]))), 6000000))
                    elif "1500 Byte 4PMD 2Q OVS/DPDK PVP test result" in line:
                        self.vsperf_ws.write_string(4, 0, '1500 Byte 4PMD 2Q DPDK', bold_format)
                        test_fail.append(self.write_throughput_pass_fail(
                            4, 1, str(int(float(line.split()[9]))), 1500000))
                    elif ("2000 Byte 2PMD OVS/DPDK PVP test result" in line or
                                  "2000 Byte 2PMD OVS/DPDK Phy2Phy test result" in line):
                        self.vsperf_ws.write_string(5, 0, '2000 Byte 2PMD 1Q DPDK', bold_format)
                        test_fail.append(self.write_throughput_pass_fail(
                            5, 1, str(int(float(line.split()[8]))), 1100000))
                    elif ("9000 Byte 2PMD OVS/DPDK PVP test result" in line or
                                  "9000 Byte 2PMD OVS/DPDK Phy2Phy test result" in line):
                        self.vsperf_ws.write_string(6, 0, '9000 Byte 2PMD 1Q DPDK', bold_format)
                        test_fail.append(self.write_throughput_pass_fail(
                            6, 1, str(int(float(line.split()[8]))), 250000))
                    elif "64   Byte OVS Kernel PVP test result" in line:
                        self.vsperf_ws.write_string(7, 0, '64 Byte Kernel',bold_format)
                        test_fail.append(self.write_throughput_pass_fail(
                            7, 1, str(int(float(line.split()[8]))), 100000))
                    elif "1500 Byte OVS Kernel PVP test result" in line:
                        self.vsperf_ws.write_string(8, 0, '1500 Byte Kernel', bold_format)
                        test_fail.append(self.write_throughput_pass_fail(
                            8, 1, str(int(float(line.split()[8]))), 100000))
            elif 'vsperf_sr_iov_results' in member:
                fh1 = tar.extractfile(member)
                data = fh1.readlines()
                for line in data:
                    if "64   Byte SR_IOV PVP test result" in line:
                        self.vsperf_ws.write_string(9, 0, '64 Byte SRIOV', bold_format)
                        test_fail.append(self.write_throughput_pass_fail(
                            9, 1, str(int(float(line.split()[7]))), 10000000))
                    elif "1500 Byte SR_IOV PVP test result" in line:
                        self.vsperf_ws.write_string(10, 0, '1500 Byte SRIOV', bold_format)
                        test_fail.append(self.write_throughput_pass_fail(
                            10, 1, str(int(float(line.split()[7]))), 1500000))
        if any(test_fail):
            self.vsperf_ws.name = self.vsperf_ws.name + ' (FAIL)'
        else:
            self.vsperf_ws.name = self.vsperf_ws.name + ' (PASS)'

    def write_pvp_worksheet(self, tar_file, csv_file, worksheet, png_list):
        """
        Write out the pvp results to the specified worksheet, write pass fail on worksheet name
        :param tar_file: tar file
        :param csv_file: csv file to process inside of tar
        :param worksheet: worksheet to write to
        :param png_list: png list from CONSTANT values
        :return: return boolean if any test failed
        """
        fh = tar_file.extractfile(csv_file)
        reader = csv.reader(fh, delimiter=',', quotechar='|')
        test_fail = False
        max_column = 0
        self.row = 0
        for row in reader:
            column = 0
            try:
                if len(row) > 0 and 'cpu' not in row[0]:
                    for i in range(len(row)):
                        # try to convert to int to round.
                        try:
                            entry = int(float(row[i]))
                            if entry <= 0:
                                test_fail = True
                        except ValueError:
                            entry = row[i]
                        worksheet.write_string(self.row, column, str(entry))
                        column += 1
                    self.row += 1
                    max_column = column if column > max_column else max_column
            except IndexError:
                continue
        for png in png_list[1:2]:
            tar_file.extractall()
            worksheet.insert_image(self.row, 0, png)

        worksheet.set_column(0, max_column, 30)
        self.row = 0
        return test_fail

    def write_throughput_pass_fail(self, row, column, text, pass_value):
        """
        Write out the vsperf results to the location specified
        :param row: row in sheet
        :param column: column in sheet
        :param text: result text
        :param pass_value: minimum value to pass for the result
        :return: Boolean if test was a failure
        """
        fail_format = self._workbook.add_format()
        fail_format.set_color('red')

        if int(text) < pass_value:
            self.vsperf_ws.write_string(row, column, text, fail_format)
            return True
        else:
            self.vsperf_ws.write_string(row, column, text)
            return False

    #
    # Calculate wire utilization based on packet size and packets per
    # seconds
    #
    # Packet size = 12 bytes IFG +
    #                8 bytes preamble +
    #                x bytes packet +
    #                4 bytes CRC
    #
    def _eth_utilization(self, line_speed_bps, packet_size,
                         packets_per_second):

        packet_size_bits = (12 + 8 + packet_size + 4) * 8
        packet_speed_second = packet_size_bits * packets_per_second

        util = float(packet_speed_second) / line_speed_bps * 100

        if util > 100:
            util = 100

        return util

    def write_tc_throughput_worksheet(self, tar_file, csv_file):
        fh = tar_file.extractfile(csv_file)
        reader = csv.reader(fh, delimiter=',', quotechar='|')
        nic_speed = None
        packet_sizes = None
        tenK_results = None
        failure = False
        for row in reader:

            if len(row) == 0:
                #
                # Empty line means new test results (we should have only one)
                #
                packet_sizes = None
                tenK_results = None
            elif nic_speed is None:
                #
                # We need the NIC speed
                #
                if row[0] == '\"Physical port':
                    nic_speed = row[2].split()[1]
                    if nic_speed not in ['10', '25', '40', '50', '100']:
                        raise ValueError(
                            "Unsupported link rate, please report!!")
                    nic_speed = int(nic_speed)

            elif packet_sizes is None:
                #
                # See if this is the line with the packet size info
                #
                if len(row) >= 2 and row[0] == 'Number of flows':
                    try:
                        packet_sizes = [int(i) for i in row[1:]]
                    except ValueError:
                        packet_sizes = None
            else:
                #
                # Here we are processing results
                #
                if (len(row) == len(packet_sizes) + 1):
                    try:
                        results_values = [int(float(i)) for i in row]
                    except ValueError:
                        if row[0].startswith("cpu_"):
                            #
                            # If line starts with cpu_x it's the embedded
                            # cpu statistics which we should ignore those
                            #
                            continue
                        else:
                            #
                            # Rest are real issues, start over...
                            #
                            packet_sizes = None
                            continue
                    #
                    # Normal result line processing
                    #
                    if results_values[0] == 10000:
                        tenK_results = results_values[1:]
                        break

        if nic_speed is None or packet_sizes is None or tenK_results is None:
            raise ValueError("The TC L3 PVP results is missing data, i.e. "
                             "Link speed, or 10K packet results!!")

        #
        # Write default workbook layout
        #
        self.pvp_tc_troughput_ws.set_column(0, 2, 16)
        self.pvp_tc_troughput_ws.set_column(2, 3, 32)
        self.pvp_tc_troughput_ws.set_column(3, 3, 40)
        self.pvp_tc_troughput_ws.set_column(4, 4, 53)
        self.pvp_tc_troughput_ws.set_column(5, 5, 38)

        bold_format = self._workbook.add_format()
        red_format = self._workbook.add_format()
        bold_format.set_bold()
        red_format.set_color('red')

        self.pvp_tc_troughput_ws.write_string(
            0, 0,
            "PVP test for 10K TC Flower rules with NIC speed of {} Gbps".
            format(nic_speed),
            bold_format)

        self.pvp_tc_troughput_ws.write_string(2, 2, "Pass criteria",
                                              bold_format)
        self.pvp_tc_troughput_ws.write_string(3, 0, "Packet Size", bold_format)
        self.pvp_tc_troughput_ws.write_string(3, 1, "pps", bold_format)

        for i, pkt_size in enumerate(packet_sizes):
            self.pvp_tc_troughput_ws.write_string(i + 4, 0, str(pkt_size))
            self.pvp_tc_troughput_ws.write_string(i + 4, 1,
                                                  str(tenK_results[i]))
        #
        # Pass criteria #1: Minimal pps based on link speed
        #
        min_pps = {10: 4528985, 25: 5874060, 40: 6345177, 50: 7931472,
                   100: 11973180}

        self.pvp_tc_troughput_ws.write_string(3, 2,
                                              "#1 minimal {} pps for {} Gbps".
                                              format(min_pps[nic_speed],
                                                     nic_speed),
                                              bold_format)

        pps_pass_index = -1
        for i, pps in enumerate(tenK_results):
            if pps >= min_pps[nic_speed]:
                if pps_pass_index == -1:
                    pps_pass_index = i
                elif pps > tenK_results[pps_pass_index]:
                    pps_pass_index = i

        if pps_pass_index == -1:
            failure = True
            for i, pps in enumerate(tenK_results):
                self.pvp_tc_troughput_ws.write_string(
                    i + 4, 2, str(pps), red_format)
        else:
            self.pvp_tc_troughput_ws.write_string(
                pps_pass_index + 4, 2, str(tenK_results[pps_pass_index]))

        #
        # Pass criteria #2: All pkt_sizes below the pps_pass_index must have a
        #                   95% or higher throughput.
        #

        self.pvp_tc_troughput_ws.write_string(
            3, 3,
            "#2 results below #1 should be >=95% of pps of #1",
            bold_format)

        if pps_pass_index == -1:
            for i, pps in enumerate(tenK_results):
                self.pvp_tc_troughput_ws.write_string(
                    i + 4, 3, "#1 not met, skipped", red_format)
        else:
            for i, pps in enumerate(tenK_results):
                if i < pps_pass_index:
                    percentage = pps / float(tenK_results[pps_pass_index]) \
                        * 100
                    if percentage < 95:
                        failure = True
                        self.pvp_tc_troughput_ws.write_string(
                            i + 4, 3, "{:.2f}".format(percentage), red_format)
                    else:
                        self.pvp_tc_troughput_ws.write_string(
                            i + 4, 3, "{:.2f}".format(percentage))
                else:
                    self.pvp_tc_troughput_ws.write_string(i + 4, 3, "-")

        #
        # Pass criteria #3: All pkt_sizes above the pps_pass_index must have
        #                   the same or higher line utilization
        #
        self.pvp_tc_troughput_ws.write_string(
            3, 4,
            "#3 results above #1 must have higher or the same line "
            "utilization", bold_format)

        if pps_pass_index == -1:
            for i, pps in enumerate(tenK_results):
                self.pvp_tc_troughput_ws.write_string(
                    i + 4, 4, "#1 not met, skipped", red_format)
        else:
            pass_percentage = self._eth_utilization(
                nic_speed * 1000000000,
                packet_sizes[pps_pass_index],
                tenK_results[pps_pass_index])

            for i, pps in enumerate(tenK_results):
                if i > pps_pass_index:
                    percentage = self._eth_utilization(nic_speed * 1000000000,
                                                       packet_sizes[i], pps)
                    if percentage < pass_percentage:
                        failure = True
                        self.pvp_tc_troughput_ws.write_string(
                            i + 4, 4, "{:.2f}".format(percentage), red_format)
                    else:
                        self.pvp_tc_troughput_ws.write_string(
                            i + 4, 4, "{:.2f}".format(percentage))
                elif i == pps_pass_index:
                    self.pvp_tc_troughput_ws.write_string(
                        i + 4, 4,
                        "{:.2f}".format(pass_percentage))
                else:
                    self.pvp_tc_troughput_ws.write_string(i + 4, 4, "-")

        #
        # Pass criteria #4: Wire speed <40G NICs
        #
        min_wire_speed_size = 0
        if nic_speed < 40:
            if nic_speed == 10:
                min_wire_speed_size = 256
            else:
                min_wire_speed_size = 512
            self.pvp_tc_troughput_ws.write_string(
                3, 5, "#4 Wire speed for {} bytes packets and larger".
                format(min_wire_speed_size), bold_format)
        else:
            self.pvp_tc_troughput_ws.write_string(
                3, 5, "#4 Wire speed tests for NICs with < 40Gbps throughput",
                bold_format)

        for i, pps in enumerate(tenK_results):
            percentage = self._eth_utilization(nic_speed * 1000000000,
                                               packet_sizes[i], pps)

            if packet_sizes[i] < min_wire_speed_size:
                self.pvp_tc_troughput_ws.write_string(i + 4, 5, "-")
            elif percentage < 95 and min_wire_speed_size != 0:
                failure = True
                self.pvp_tc_troughput_ws.write_string(
                    i + 4, 5, "{:.2f}".format(percentage), red_format)
            else:
                self.pvp_tc_troughput_ws.write_string(
                    i + 4, 5, "{:.2f}".format(percentage))

        return failure

    def process_tc_flower_result(self):
        """
        write the tc flower to work sheet
        :return: Boolean if test was a failure
        """
        def get_average_rate(data_file):
            rate_list = []
            entry_list = []
            if os.path.exists(data_file):
                with open("fl_change.dat") as fd:
                    all_data_list = fd.read().split("\n\n")
                    for data in all_data_list:
                        if data is not None and \
                           data not in ['\n', '\r', '\r\n']:
                            data_list = data.strip('\n').split('\n')
                            begin_time = data_list[0].split(" ")[0]
                            end_time, total_rule = data_list[-1].split(" ")
                            total_time = float(end_time) - float(begin_time)
                            try:
                                rate = int(total_rule) / total_time
                                rate_list.append(rate)
                            except:
                                rate = int(total_rule)
                                rate_list.append(rate)
                            pass
                            entry_list.append(len(data_list))
                        else:
                            pass
                pass
            else:
                print("Can not find the data file")
            return rate_list, entry_list

        row = 0
        column = 0
        failure = False
        data_file = "fl_change.dat"
        test_names = ["Cumulative", "SW only", "HW only", "Just flower"]
        if os.path.exists(data_file):
            self.flower_rule_ws = self._workbook.add_worksheet(
                'tc-flower insert rate')
            bold_format = self._workbook.add_format()
            bold_format.set_bold()
            self.flower_rule_ws.set_column(0, 3, 16)

            # setup column headers and passing result column
            self.flower_rule_ws.write_string(row, column + 1, "Average rate per sec",
                                             bold_format)
            self.flower_rule_ws.write_string(row, column + 2, "Insertions",
                                             bold_format)
            self.flower_rule_ws.write_string(row, column + 3,
                                             "Required to pass", bold_format)
            self.flower_rule_ws.write_string(row + 1, column + 3,
                                             "1.5k/s average rate")
            self.flower_rule_ws.write_string(row + 3, column + 3,
                                             "10K concurrent hardware flows")

            row += 1
            rate_list, entry_list = get_average_rate(data_file)
            if rate_list:
                for index, rate in enumerate(rate_list):
                    if index < len(test_names):
                        label = test_names[index]
                    else:
                        label = "Test %d" % (index+1)

                    self.flower_rule_ws.write_string(row, column, label,
                                                     bold_format)

                    if index == 0 and rate < 1500:
                        fail_format = self._workbook.add_format()
                        fail_format.set_color('red')

                        self.flower_rule_ws.write_string(row, column + 1,
                                                         str(rate),
                                                         fail_format)
                        failure = True
                    else:
                        self.flower_rule_ws.write_string(row, column + 1,
                                                         str(rate))

                    if index == 2 and entry_list[index] < 10000:
                        fail_format = self._workbook.add_format()
                        fail_format.set_color('red')

                        self.flower_rule_ws.write_string(row, column + 2,
                                                         str(entry_list[index]),
                                                         fail_format)
                        failure = True
                    else:
                        self.flower_rule_ws.write_string(row, column + 2,
                                                         str(entry_list[index]))

                    row += 1
        else:
            self.flower_rule_ws = None
            return False

        if failure:
            self.flower_rule_ws.name = self.flower_rule_ws.name + ' (FAIL)'
        else:
            self.flower_rule_ws.name = self.flower_rule_ws.name + ' (PASS)'

        if os.path.exists('fl_change.png'):
            self.flower_rule_ws.insert_image(row + 3, 0, 'fl_change.png')
            return True
        else:
            return False


def main():
    mysheet = ResultsSheet(args)
    mysheet.process_throughput_results()
    mysheet.process_functional_results()
    mysheet.process_pvp_results()
    mysheet.process_tc_flower_result()
    mysheet.close_workbook()


def yes_no(answer):
    yes = set(['yes', 'y', 'ye', ''])
    no = set(['no', 'n'])

    while True:
        choice = raw_input(answer).lower()
        if choice in yes:
            return True
        elif choice in no:
            return False
        else:
            print("Please respond with 'yes' or 'no'\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='Output file name')
    parser.add_argument('-s', '--server_tar_file', type=str, required=True,
                        help='Server tar file name')
    parser.add_argument('-c', '--client_tar_file', type=str, required=True,
                        help='Client tar file name')
    args = parser.parse_args()
    if os.path.isfile(args.output):
        ans = yes_no("Output file {} already exists. Overwrite?".format(args.output))
        if not ans:
            sys.exit()
    if os.path.isfile(args.server_tar_file) == False or os.path.isfile(args.client_tar_file) == False:
        print("Server or client file do not exist. Check your arguments.")
    main()
