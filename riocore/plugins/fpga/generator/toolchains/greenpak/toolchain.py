import importlib
import os
import shutil
import sys


class Toolchain:
    def __init__(self, config):
        self.config = config
        self.gateware_path = self.config["output_path"]
        self.riocore_path = config["riocore_path"]
        self.toolchain_path = self.config.get("toolchains_json", {}).get("ise", "")
        if self.toolchain_path and not self.toolchain_path.endswith("lin64"):
            self.toolchain_path = os.path.join(self.toolchain_path, "bin", "lin64")

    @classmethod
    def info(cls):
        return {
            "url": "https://renesasweb-greenpak.s3.us-west-2.amazonaws.com/v6.53/go-configure-sw-hub-v6.53.003-debian-12-amd64.deb",
            "info": "Renesas - GreenPack",
            "description": """
using https://github.com/trholding/shrike-gen for makefile support
""",
        }

    def generate(self, path):
        shrike_path = os.path.join(path, "shrike")
        shrike_gen = os.path.join(os.path.dirname(__file__), "shrike_gen")
        if not os.path.exists(shrike_path):
            shutil.copytree(shrike_gen, shrike_path)

        src_path = os.path.join(shrike_path, "ffpga", "src")
        os.makedirs(src_path, exist_ok=True)
        build_path = os.path.join(shrike_path, "ffpga", "build")
        os.makedirs(build_path, exist_ok=True)

        pins_generator = importlib.import_module(".pins", "riocore.plugins.fpga.generator.pins.pcf")
        pins_generator.Pins(self.config).generate(path, shrike=True)

        if sys.platform == "linux":
            ngdbuild = shutil.which("GPLauncher")
            if ngdbuild is None:
                print("WARNING: can not found toolchain installation in PATH: GreenPack (GPLauncher)")
                print("  example: export PATH=$PATH:/opt/GreenPack/bin/")

        ffpga_data = """<?xml version="1.0" encoding="UTF-8"?>
<GPDProject version="40" oldestCompatibleVersion="32" GPDVersion="6.53.003" lastChange="1 Jun 2026 00:00:00" projectChecksumState="0" projectChecksum="00000000">
    <Metadata>
        <LegalNotice>Generated with riocore</LegalNotice>
    </Metadata>
    <generalProjectSettings/>
    <chip family="04" type="06" friendlyName="FFPGA" partNumber="67" package="26">
        <nvmData registerLenght="480">0 0 0 28 0 0 0 0 A5 A5 A5 A5 0 0 0 0 0 0 0 0 5A 5A 5A 5A 0 0 0 0 22 22 22 22 22 22 22 22 22 22 0 0 3 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0</nvmData>
        <checksum crc32="0x451C1D42" version="2"/>
        <virtualProperties/>
    </chip>
    <fpga-data>
        <project-data-version>8</project-data-version>
        <oldestCompatibleVersion>8</oldestCompatibleVersion>
        <settings>
            <generateBitstream>
                <MAX_CPU>16</MAX_CPU>
                <additionalArguments></additionalArguments>
                <clockConcurrentOptimization>true</clockConcurrentOptimization>
                <compilerVersion>23</compilerVersion>
                <highDensityIOPacking>false</highDensityIOPacking>
                <highDensityPackingLogic>true</highDensityPackingLogic>
                <maximumRoutingIterations>300</maximumRoutingIterations>
                <placeAndTrialRoute>false</placeAndTrialRoute>
                <placeAndTrialRouteIterationCount>20</placeAndTrialRouteIterationCount>
                <timingAnalysisCorner>0</timingAnalysisCorner>
                <timingAnalysisLimitPaths>-1</timingAnalysisLimitPaths>
            </generateBitstream>
            <synthesize>
                <additionalArguments></additionalArguments>
                <autoname>true</autoname>
                <enableHardMultiplexerResources>false</enableHardMultiplexerResources>
                <flatten>true</flatten>
                <keep>false</keep>
                <multiplexerResourcesNumber>5</multiplexerResourcesNumber>
                <noDSP>true</noDSP>
                <noFSM>false</noFSM>
                <useABC9>true</useABC9>
                <yosysVersion>59</yosysVersion>
            </synthesize>
        </settings>
        <modules>
            <scr>
                <module filename="rio.v"/>
                <module filename="uart_baud.v"/>
                <module filename="uart_rx.v"/>
                <module filename="uart_tx.v"/>
                <module filename="uart.v"/>
            </scr>
        </modules>
        <io-spec-tool></io-spec-tool>
        <pllConfigurator>
            <pllConfiguratorDataVersion>1</pllConfiguratorDataVersion>
            <pllConfigurations>
                <pllConfiguration>
                    <pllFref>50.000000</pllFref>
                    <pllIsManualCalculationMode>0</pllIsManualCalculationMode>
                    <pllOutputChannels>
                        <pllOutputChannel>
                            <pllIsOutEnabled>1</pllIsOutEnabled>
                            <pllRequiredFout>50.000000</pllRequiredFout>
                            <pllRefDiv>1</pllRefDiv>
                            <pllFbDiv>25</pllFbDiv>
                            <pllPostDiv1>5</pllPostDiv1>
                            <pllPostDiv2>5</pllPostDiv2>
                        </pllOutputChannel>
                    </pllOutputChannels>
                    <pllProperties>
                        <pllBypass>0</pllBypass>
                        <pllClockSelection>0</pllClockSelection>
                        <pllEnableUserClockByPll>0</pllEnableUserClockByPll>
                        <pllLock>0</pllLock>
                    </pllProperties>
                </pllConfiguration>
            </pllConfigurations>
        </pllConfigurator>
    </fpga-data>
    <projectData>
        <specs>
            <lastModify lastModifyValue="01.06.2026 00:00:00"/>
            <vddSpecs vddMin="1.05" vddTyp="1.1" vddMax="1.15"/>
            <vdd2Specs vdd2Min="1.71" vdd2Typ="2.5" vdd2Max="3.465"/>
            <tempSpecs tempMin="-40" tempTyp="30" tempMax="85"/>
        </specs>
    </projectData>
</GPDProject>
"""
        open(os.path.join(shrike_path, "rio.ffpga"), "w").write(ffpga_data)

        smk_data = []
        smk_data.append("PROJECT := rio")
        smk_data.append("TOP     := rio")
        smk_data.append("")
        open(os.path.join(shrike_path, "shrike.mk"), "w").write("\n".join(smk_data))

        makefile_data = []
        makefile_data.append("")
        makefile_data.append("all: build")
        makefile_data.append("")
        makefile_data.append("clean:")
        makefile_data.append("	cd shrike/ffpga/build/ && rm -rf *.v *.edif *.ys *.txt *.log *.bin *.sdc *.vm *.prj bitstream minplacer ta_message")
        makefile_data.append("")
        makefile_data.append("build:")
        makefile_data.append("	ln -f *.v shrike/ffpga/src/")
        makefile_data.append("	cd shrike && make update pnr")
        makefile_data.append("")
        open(os.path.join(path, "Makefile"), "w").write("\n".join(makefile_data))

        floorplan_data = []
        floorplan_data.append("1K")
        floorplan_data.append("")
        floorplan_data.append("M")
        floorplan_data.append("")
        open(os.path.join(shrike_path, "ffpga", "build", "floorplanspec.fp"), "w").write("\n".join(floorplan_data))

        smake_data = open(os.path.join(shrike_gen, "Makefile"), "r").read()
        smake_data = smake_data.replace("synth: lint", "synth:")
        smake_data = smake_data.replace("/opt/go-configure-sw-hub", "/usr/local/go-configure-sw-hub")
        smake_data = smake_data.replace('read_verilog -sv "../src/main.v"', f"read_verilog -sv ../src/{' ../src/'.join(self.config['verilog_files'])}")
        smake_data = smake_data.replace("VSRC       := main.v", "VSRC       := rio.v")
        open(os.path.join(shrike_path, "Makefile"), "w").write(smake_data)
