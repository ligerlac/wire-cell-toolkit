#!/usr/bin/env python

# Copyright 2015-2023 Brookhaven National Laboratory for the benefit
# of the Wire-Cell Team.
# 
# This file is part of the wire-cell-toolkit project and distributed
# according to the LICENSE file provided as also part of this project.

import os

# fixme: move into waft/
from waflib.Build import BuildContext
from waflib.Logs import debug, info, error, warn
import waflib.Utils

TOP = '.'
APPNAME = 'WireCell'
VERSION = os.popen("git describe --tags").read().strip()

# to avoid adding tooldir="waft" in all the load()'s
import os
import sys
sys.path.insert(0, os.path.realpath("./waft"))

def options(opt):
    opt.load("wcb")

    # this used in cfg/wscript_build
    opt.add_option('--install-config', type=str, default="",
                   help="Install configuration files for given experiment")

    # fixme: add to spdlog entry in wcb.py
    opt.add_option('--with-spdlog-static', type=str, default="yes",
                   help="Def is true, set to false if your spdlog is not compiled (not recomended)")

def configure(cfg):
    # Save to BuildConfig.h and env
    cfg.define("WIRECELL_VERSION", VERSION)
    cfg.env.VERSION = VERSION

    # See comments at top of Exceptions.h for context.
    cfg.load('compiler_cxx')
    cfg.check_cxx(lib='backtrace', use='backtrace',
                  uselib_store='BACKTRACE',
                 define_name = 'HAVE_BACKTRACE_LIB',
                 mandatory=False, fragment="""
#include <backtrace.h>
int main(int argc,const char *argv[])
{
    struct backtrace_state *state = backtrace_create_state(nullptr,false,nullptr,nullptr);
}
                 """)
    if cfg.is_defined('HAVE_BACKTRACE_LIB'):
        cfg.env.LDFLAGS += ['-lbacktrace']

    # fixme: this should go away when everyone is up to at least boost
    # 1.78.
    cfg.check_cxx(header_name="boost/core/span.hpp", use='boost',
                  define_name = 'HAVE_BOOST_CORE_SPAN_HPP',
                  mandatory=False)


    # boost 1.59 uses auto_ptr and GCC 5 deprecates it vociferously.
    cfg.env.CXXFLAGS += ['-Wno-deprecated-declarations']
    cfg.env.CXXFLAGS += ['-Wall', '-Wno-unused-local-typedefs', '-Wno-unused-function']
    # cfg.env.CXXFLAGS += ['-Wpedantic', '-Werror']
    cfg.env.CXXFLAGS += ['-std=c++17']

    # this fixes 'Boost.Stacktrace requires `_Unwind_Backtrace` function.'
    cfg.env.CXXFLAGS += ['-DBOOST_STACKTRACE_GNU_SOURCE_NOT_REQUIRED=1']
    
    if cfg.options.with_spdlog_static.lower() in ("yes","on","true"):
        cfg.env.CXXFLAGS += ['-DSPDLOG_COMPILED_LIB=1']

    # in principle, this should be the only line here.  Any cruft
    # above that has accrued should be seen as a fixme: move to
    # wcb/waf-tools.
    cfg.load("wcb")

    cfg.env.CXXFLAGS += ['-I.']

    info("Configured version %s" % VERSION)


def build(bld):
    bld.load('wcb')

def dumpenv(bld):
    bld.load('wcb')

def packrepo(bld):
    bld.load('wcb')
