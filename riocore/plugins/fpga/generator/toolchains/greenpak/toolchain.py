import importlib
import os
import re
import shutil
import subprocess
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
        os.makedirs(shrike_path, exist_ok=True)
        src_path = os.path.join(shrike_path, "ffpga", "src")
        os.makedirs(src_path, exist_ok=True)
        build_path = os.path.join(shrike_path, "ffpga", "build")
        os.makedirs(build_path, exist_ok=True)
        shrike_gen = os.path.join(os.path.dirname(__file__), "shrike_gen")
        if not os.path.exists(os.path.join(shrike_path, "shrike_gen")):
            shutil.copytree(shrike_gen, os.path.join(shrike_path, "shrike_gen"))

        pins_generator = importlib.import_module(".pins", "riocore.plugins.fpga.generator.pins.pcf")
        pins_generator.Pins(self.config).generate(path, shrike=True)

        if sys.platform == "linux":
            ngdbuild = shutil.which("GPLauncher")
            if ngdbuild is None:
                print("WARNING: can not found toolchain installation in PATH: GreenPack (GPLauncher)")
                print("  example: export PATH=$PATH:/opt/GreenPack/bin/")

        verilogs = " ".join(self.config["verilog_files"])

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
                <module filename="main.v"/>
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
        makefile_data.append("	ls")
        makefile_data.append("")
        makefile_data.append("build:")
        makefile_data.append("	cat *.v > shrike/ffpga/src/main.v")
        makefile_data.append("	cd shrike && make update pnr")
        makefile_data.append("")
        open(os.path.join(path, "Makefile"), "w").write("\n".join(makefile_data))

        floorplan_data = []
        floorplan_data.append("1K")
        floorplan_data.append("")
        floorplan_data.append("M")
        floorplan_data.append("")
        open(os.path.join(shrike_path, "ffpga", "build", "floorplanspec.fp"), "w").write("\n".join(floorplan_data))

        smake_data = """# Vulcan's Makefile for SLG47910V / Shrike Lite, part of shrike-gen
#
# Role-aware: automatically detects workspace vs project context.
# A project directory is identified by the presence of a *.ffpga file.
#
# ── WORKSPACE MODE (no *.ffpga here) ─────────────────────────────────────────
#   make init                  create ./shrike-gen symlink (optional)
#   make project ProjectName   create a new project skeleton
#   make project NAME=Name     (alternative syntax)
#   make list                  list existing projects
#   make help                  show this message
#
# ── PROJECT MODE (*.ffpga present) ───────────────────────────────────────────
#   make              update + full build
#   make update       regenerate .ffpga and io_spec_in.txt from io_map.pcf
#   make build        lint → synth → pnr → collect (skip update)
#   make lint         verilator lint only
#   make synth        synthesis only
#   make clean        remove all build outputs (keeps source + constraints)
#   make help         show this message

# ── Context detection ─────────────────────────────────────────────────────────
# The presence of a *.ffpga file is the canonical marker for a project dir.
_FFPGA_FILE := $(firstword $(wildcard *.ffpga))

ifeq (,$(_FFPGA_FILE))
# =============================================================================
# WORKSPACE MODE
# =============================================================================

SHRIKE_GEN := shrike_gen/shrike-gen.py

.DEFAULT_GOAL := help

.PHONY: init project _project list help

# ── make init ─────────────────────────────────────────────────────────────────
init:
	@if [ -e shrike-gen ]; then \
		echo "  shrike-gen already exists — skipping"; \
	else \
		chmod +x shrike_gen/shrike-gen.py; \
		ln -sf shrike_gen/shrike-gen.py shrike-gen; \
		echo "  Symlink created: ./shrike-gen → shrike_gen/shrike-gen.py"; \
	fi

# ── make project [NAME=]ProjectName ──────────────────────────────────────────
# Also supports positional form: make project MyBlink
# The word after "project" on the command line is captured as a Make target
# (which would normally fail); the catch-all rule below silences it.
_POSITIONAL_NAME := $(filter-out project,$(MAKECMDGOALS))

project: _project
_project:
	@name="$(or $(NAME),$(_POSITIONAL_NAME))"; \
	if [ -z "$$name" ]; then \
		echo ""; \
		echo "  Usage:  make project NAME=<ProjectName>"; \
		echo "          make project <ProjectName>"; \
		echo ""; \
		exit 1; \
	fi; \
	python3 $(SHRIKE_GEN) "$$name"

# Swallow the positional project name so Make doesn't error on an unknown target
$(filter-out project list help _project init,$(MAKECMDGOALS)):
	@:

# ── make list ─────────────────────────────────────────────────────────────────
list:
	@echo ""
	@echo "  Projects in $(CURDIR):"
	@for d in */Makefile; do \
		proj=$$(dirname $$d); \
		ffpga=$$proj/*.ffpga; \
		[ -f $$ffpga ] && echo "    $$proj" || true; \
	done
	@echo ""

# ── make help ─────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "  Shrike Lite / SLG47910V shrike-gen"
	@echo ""
	@echo "  make init                  create ./shrike-gen symlink (optional)"
	@echo "  make project ProjectName   create a new project"
	@echo "  make project NAME=Name     (alternative syntax)"
	@echo "  make list                  list existing projects"
	@echo ""
	@echo " cd ProjectName"
	@echo ""
	@echo " Then, inside the project:"
	@echo "    Edit ffpga/src/main.v           edit Verilog"
	@echo "    Edit io_map.pcf                 edit pin constraints"
	@echo "    make                            update + full build"
	@echo "    make update                     regenerate .ffpga + io_spec_in.txt"
	@echo "    make build                      build only (skip update)"
	@echo "    make clean                      clean build outputs"
	@echo ""
	@echo "  Bitstreams land in: ProjectName/ffpga/build/bitstream/"
	@echo "    FPGA_bitstream_MCU.bin"
	@echo "    FPGA_bitstream_OTP.bin"
	@echo "    FPGA_bitstream_FLASH_MEM.bin"
	@echo ""

else
# =============================================================================
# PROJECT MODE  —  identity comes from shrike.mk (written by shrike-gen)
# =============================================================================

include shrike.mk

# ── Directories ───────────────────────────────────────────────────────────────
PROJECT_DIR := $(CURDIR)
SRC_DIR     := $(PROJECT_DIR)/ffpga/src
BUILD_DIR   := $(PROJECT_DIR)/ffpga/build
TOOLS_DIR   := $(PROJECT_DIR)/shrike_gen

# ── Generator scripts ─────────────────────────────────────────────────────────
GEN_IO_SPEC    := $(TOOLS_DIR)/gen_io_spec.py
GEN_FFPGA      := $(TOOLS_DIR)/gen_ffpga.py
GEN_FPGA_DATA  := $(TOOLS_DIR)/gen_fpga_data.py
GEN_BITSTREAMS := $(TOOLS_DIR)/gen_bitstreams.py

# ── Tool binaries (Go Configure Software Hub) ─────────────────────────────────
GCSW        := /usr/local/go-configure-sw-hub/bin/external
YOSYS       := $(GCSW)/yosys/v59/yosys
VERILATOR   := $(GCSW)/verilator/bin/verilator_bin
EDA_PLACER  := $(GCSW)/eda-placer/v23/eda-placer

VERILATOR_ROOT         := $(GCSW)/verilator
EFLX_COMPILER_INSTALL  := $(GCSW)/eda-placer/v23
export VERILATOR_ROOT
export EFLX_COMPILER_INSTALL

# ── Sources / constraints / outputs ───────────────────────────────────────────
VSRC       := main.v
PCF        := $(PROJECT_DIR)/io_map.pcf
IO_SPEC    := $(BUILD_DIR)/io_spec_in.txt
FLOOR_PLAN := $(BUILD_DIR)/floorplanspec.fp
FFPGA      := $(PROJECT_DIR)/$(PROJECT).ffpga
NETLIST    := $(BUILD_DIR)/netlist.edif
SYNTH_YS   := $(BUILD_DIR)/synth_script.ys

.DEFAULT_GOAL := all

.PHONY: all update build lint synth pnr collect clean check-tools help

# ── all: update then full build ───────────────────────────────────────────────
all: update build

# ── update: regenerate .ffpga and io_spec_in.txt from io_map.pcf ──────────────
update: $(PCF) $(BUILD_DIR)
	@echo "=== Update: generating io_spec_in.txt and $(PROJECT).ffpga ==="
	python3 $(GEN_IO_SPEC) \
		--pcf        $(PCF) \
		--out-iospec $(IO_SPEC)
	python3 $(GEN_FFPGA) \
		--project    $(PROJECT) \
		--sources    $(VSRC) \
		--pcf        $(PCF) \
		--max-cpu    $$(nproc) \
		--out        $(FFPGA)
	@echo "Update OK"

# ── build: full pipeline (lint → synth → pnr → collect) ──────────────────────
build: check-tools pnr

# ── check-tools: verify external binaries and generated inputs exist ──────────
check-tools:
	@test -x $(YOSYS)      || (echo "ERROR: yosys not found at $(YOSYS)";           exit 1)
	@test -x $(VERILATOR)  || (echo "ERROR: verilator not found at $(VERILATOR)";   exit 1)
	@test -x $(EDA_PLACER) || (echo "ERROR: eda-placer not found at $(EDA_PLACER)"; exit 1)
	@test -f $(IO_SPEC)    || (echo "ERROR: io_spec_in.txt missing — run: make update"; exit 1)
	@test -f $(FLOOR_PLAN) || (echo "ERROR: floorplanspec.fp missing in $(BUILD_DIR)"; exit 1)
	@echo "Tools OK"

# ── lint ──────────────────────────────────────────────────────────────────────
lint: check-tools
	@echo "=== Lint ==="
	cd $(SRC_DIR) && verilator \
		+1364-2005ext+.v \
		-I$(SRC_DIR) \
		--lint-only \
		--timing \
		$(VSRC) || true
	@echo "Lint OK"

# ── synth ─────────────────────────────────────────────────────────────────────
define SYNTH_SCRIPT
read_verilog -sv "../src/main.v"
hierarchy -check
flatten -noscopeinfo
synth_xilinx -nobram -noiopad -nodsp -abc9
clean
autoname
write_verilog "post_synth_results.v"
write_edif "netlist.edif"
tee -q -o post_synth_report.txt stat
endef

synth: lint $(NETLIST)

$(NETLIST): $(SRC_DIR)/$(VSRC) | $(BUILD_DIR)
	@echo "=== Synthesis ==="
	$(file >$(SYNTH_YS),$(SYNTH_SCRIPT))
	cd $(BUILD_DIR) && $(YOSYS) \
		-e '(.*)is implicitly declared\.' \
		-Q \
		-s synth_script.ys
	@echo "Synthesis OK — netlist: $(NETLIST)"

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)/bitstream $(BUILD_DIR)/ta_message

# ── pnr: place & route, then collect ─────────────────────────────────────────
pnr: synth
	@echo "=== Place & Route ==="
	$(eval RUNDIR := $(shell mktemp -d /tmp/eflx_XXXXXXXX))
	mkdir -p $(RUNDIR)/config $(RUNDIR)/out
	cp $(IO_SPEC)    $(RUNDIR)/config/io_spec_in.txt
	cp $(FLOOR_PLAN) $(RUNDIR)/config/floorplanspec.fp
	$(eval FPGA_DATA_BLOB := $(shell python3 $(GEN_FPGA_DATA) \
		--netlist $(NETLIST) \
		--fp      $(RUNDIR)/config/floorplanspec.fp \
		--io      $(RUNDIR)/config/io_spec_in.txt))
	@set -o pipefail; \
	 cd $(RUNDIR)/out && $(EDA_PLACER) FPGA_DATA '$(FPGA_DATA_BLOB)' 0 \
		2>&1 | tee $(BUILD_DIR)/PNR_STDOUT.log \
	|| { echo "ERROR: eda-placer failed — see $(BUILD_DIR)/PNR_STDOUT.log"; exit 1; }
	@echo "=== Collecting results ==="
	$(MAKE) collect RUNDIR=$(RUNDIR)
	@echo "PnR OK"

# ── collect: gather eda-placer outputs into ffpga/build/ ─────────────────────
collect:
	@test -n "$(RUNDIR)" || (echo "ERROR: RUNDIR not set"; exit 1)
	@for eflx in $(RUNDIR)/out/EFLX_*.bin $(RUNDIR)/out/EFLX_*.log $(RUNDIR)/out/EFLX_*.sdc; do \
		[ -f "$$eflx" ] || continue; \
		base=$$(basename "$$eflx"); \
		fpga=$$(echo "$$base" | sed 's/EFLX_/FPGA_/'); \
		cp "$$eflx" "$(BUILD_DIR)/$$fpga"; \
		echo "  $$base → $$fpga"; \
	done
	@for f in \
		FPGA_bitstream.bin FPGA_bitstream.log FPGA_bitstream_AXI.log \
		FPGA_case_analysis_RBB.sdc FPGA_case_analysis_top1per.sdc \
		PNR_PACK_PLACE.log PNR_TIMING.log PNR_ROUTE.log PNR_IO.log \
		PNR_PLACER_REGION.log PNR_PLACER_RESOURCE.log PNR_PLACER_TIMING.log \
		clock_tree.txt resource-utilization-report.log \
		$(TOP)_eflx_array_wrapper.vm; do \
		test -f $(RUNDIR)/out/$$f && cp $(RUNDIR)/out/$$f $(BUILD_DIR)/ || true; \
	done
	@if [ -d $(RUNDIR)/out/minplacer ]; then \
		mkdir -p $(BUILD_DIR)/minplacer; \
		cp -r $(RUNDIR)/out/minplacer/. $(BUILD_DIR)/minplacer/; \
	fi
	@if [ -d $(RUNDIR)/out/ta_message ]; then \
		mkdir -p $(BUILD_DIR)/ta_message; \
		cp -r $(RUNDIR)/out/ta_message/. $(BUILD_DIR)/ta_message/; \
	fi
	@if [ -f "$(BUILD_DIR)/FPGA_bitstream_AXI.log" ]; then \
		mkdir -p $(BUILD_DIR)/bitstream; \
		python3 $(GEN_BITSTREAMS) \
			--axi     $(BUILD_DIR)/FPGA_bitstream_AXI.log \
			--outdir  $(BUILD_DIR)/bitstream \
			--project $(PROJECT) \
			--netlist netlist.edif; \
	fi
	@echo "Collected outputs to $(BUILD_DIR)"

# ── clean ─────────────────────────────────────────────────────────────────────
clean:
	rm -f  $(BUILD_DIR)/netlist.edif $(BUILD_DIR)/post_synth_results.v
	rm -f  $(BUILD_DIR)/post_synth_report.txt $(BUILD_DIR)/synth_script.ys
	rm -f  $(BUILD_DIR)/FPGA_bitstream* $(BUILD_DIR)/EFLX_bitstream* $(BUILD_DIR)/PNR_*.log
	rm -f  $(BUILD_DIR)/clock_tree.txt $(BUILD_DIR)/resource-utilization-report.log
	rm -f  $(BUILD_DIR)/FPGA_case_analysis_*.sdc $(BUILD_DIR)/*.vm
	rm -rf $(BUILD_DIR)/minplacer $(BUILD_DIR)/ta_message $(BUILD_DIR)/bitstream
	@echo "Clean OK"

# ── help ──────────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "  $(PROJECT) — SLG47910V (Shrike Lite) build"
	@echo ""
	@echo "  make          update + full build"
	@echo "  make update   regenerate .ffpga and io_spec_in.txt from io_map.pcf"
	@echo "  make build    lint → synth → pnr → collect (skip update)"
	@echo "  make lint     verilator lint only"
	@echo "  make synth    synthesis only"
	@echo "  make clean    remove build outputs"
	@echo ""
	@echo "  Edit files:"
	@echo "    ffpga/src/main.v    Verilog source"
	@echo "    io_map.pcf          pin constraints"
	@echo ""
	@echo "  Bitstreams land in: ffpga/build/bitstream/"
	@echo "    FPGA_bitstream_MCU.bin"
	@echo "    FPGA_bitstream_OTP.bin"
	@echo "    FPGA_bitstream_FLASH_MEM.bin"
	@echo ""

endif
"""
        open(os.path.join(shrike_path, "Makefile"), "w").write(smake_data)
