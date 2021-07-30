---
title: Intel Pin Tool Use Note
date: 2021-04-28 16:05:40
tags: 计算机体系结构
description: Intel Pin 使用指南
categories: 技术博客
---

<!-- TOC -->

- [Overview](#overview)
- [User's Manual](#users-manual)
- [Tutorials](#tutorials)
- [Related Content](#related-content)
- [Pin 3.18 User Guide](#pin-318-user-guide)
  - [How to Instrument with Pin](#how-to-instrument-with-pin)
    - [Pin](#pin)
    - [Pintools](#pintools)
    - [Observations](#observations)
    - [Instrumentation Granularity](#instrumentation-granularity)
    - [Managed platforms support](#managed-platforms-support)
    - [Symbols](#symbols)
    - [Floating Point Support in Analysis Routines](#floating-point-support-in-analysis-routines)
    - [Instrumenting Multi-threaded Applications](#instrumenting-multi-threaded-applications)
    - [Avoiding Deadlocks in Multi-threaded Applications](#avoiding-deadlocks-in-multi-threaded-applications)
  - [Examples](#examples)
    - [Building the Example Tools](#building-the-example-tools)
    - [Simple Instruction Count (Instruction Instrumentation)](#simple-instruction-count-instruction-instrumentation)
    - [Instruction Address Trace (Instruction Instrumentation)](#instruction-address-trace-instruction-instrumentation)
    - [Memory Reference Trace (Instruction Instrumentation)](#memory-reference-trace-instruction-instrumentation)
    - [Detecting the Loading and Unloading of Images (Image Instrumentation)](#detecting-the-loading-and-unloading-of-images-image-instrumentation)
    - [More Efficient Instruction Counting (Trace Instrumentation)](#more-efficient-instruction-counting-trace-instrumentation)
    - [Procedure Instruction Count (Routine Instrumentation)](#procedure-instruction-count-routine-instrumentation)
    - [Using PIN_SafeCopy()](#using-pin_safecopy)
    - [Order of Instrumentation](#order-of-instrumentation)
    - [Finding the Value of Function Arguments](#finding-the-value-of-function-arguments)
    - [Finding Functions By Name on Windows](#finding-functions-by-name-on-windows)
    - [Instrumenting Threaded Applications](#instrumenting-threaded-applications)
    - [Using TLS](#using-tls)
    - [Using the Fast Buffering APIs](#using-the-fast-buffering-apis)
    - [Finding the Static Properties of an Image](#finding-the-static-properties-of-an-image)
    - [Detaching Pin from the Application](#detaching-pin-from-the-application)
    - [Replacing a Routine in Probe Mode](#replacing-a-routine-in-probe-mode)
    - [Instrumenting Child Processes](#instrumenting-child-processes)
    - [Instrumenting Before and After Forks](#instrumenting-before-and-after-forks)
    - [Managed platforms support](#managed-platforms-support-1)
  - [Callbacks](#callbacks)
  - [Modifying Application Instructions](#modifying-application-instructions)
  - [The Pin Advanced Debugging Extensions](#the-pin-advanced-debugging-extensions)
  - [Applying a Pintool to an Application](#applying-a-pintool-to-an-application)
  - [Tips for Debugging a Pintool](#tips-for-debugging-a-pintool)
  - [Logging Messages from a Pintool](#logging-messages-from-a-pintool)
  - [Performance Considerations](#performance-considerations)
  - [Memory management](#memory-management)
  - [PinTools Information and Restrictions](#pintools-information-and-restrictions)
  - [Building Tools on windows](#building-tools-on-windows)
  - [Libraries for Windows](#libraries-for-windows)
  - [Libraries for Linux](#libraries-for-linux)
  - [Installation](#installation)
  - [Building Your Own Tool](#building-your-own-tool)
  - [Pin's makefile Infrastructure](#pins-makefile-infrastructure)
  - [Feedback](#feedback)
  - [Disclaimer and Legal Information](#disclaimer-and-legal-information)
  - [Pin API reference](#pin-api-reference)
  - [Pin Command Line Switches](#pin-command-line-switches)
  - [Instrumentation Library](#instrumentation-library)

<!-- /TOC -->

官方网址：https://software.intel.com/content/www/us/en/develop/articles/pin-a-dynamic-binary-instrumentation-tool.html

## Overview

Pin是用于IA-32，x86-64和MIC指令集体系结构的动态二进制工具框架，可用于创建动态程序分析工具。Intel®VTune™ Amplifier，Intel®Inspector，Intel®Advisor和Intel®软件开发仿真器（Intel®SDE）都使用Pin进行构建。使用Pin创建的称为Pintools的工具可用于在Linux *，Windows *和macOS *上的用户空间应用程序上执行程序分析。作为动态二进制检测工具，检测在运行时对已编译的二进制文件进行。因此，它不需要重新编译源代码，并且可以支持动态生成代码的检测程序。
Pin提供了丰富的API，该API提取了底层的指令集特性，并允许将诸如寄存器内容之类的上下文信息作为参数传递给注入的代码。 Pin会自动保存和恢复被注入的代码覆盖的寄存器，因此应用程序可以继续工作。 也可以访问符号和调试信息。
Pin最初是作为用于计算机体系结构分析的工具而创建的，但是其灵活的API和活跃的社区（称为“ Pinheads”）为安全性，仿真和并行程序分析创建了各种各样的工具。

## User's Manual

- [Pin 3.18 98332 Pin Manual](https://software.intel.com/sites/landingpage/pintool/docs/98332/Pin/html/)
- [Pin CRT](https://software.intel.com/sites/landingpage/pintool/docs/98332/PinCRT/PinCRT.pdf)
  - [Pin 3.18 98332 Pin OS-APIs User Guide](https://software.intel.com/sites/landingpage/pintool/docs/98332/OS-APIs/html/index.html)

## Tutorials

- [CGO 2013](Pin_Doc/cgo2013-256675.pdf) [PDF 3.464MB] (February 2013, Shenzhen, China)
- [CGO 2012/ISPASS 2012](Pin_Doc/pin-tutorial-cgo-ispass-2012.ppt) [PPT 6.7MB] (April 2012 - San Jose, CA and New Brunswick, NJ)
- [CGO 2011](Pin_Doc/pin-tutorial-cgo-2011-final-1.ppt) [PPT 10.5MB] (April 2011, Chamonix, France)
- [CGO 2010](Pin_Doc/cgo-2010-final.ppt) [PPT 7MB] (April 2010, Toronto, Canada)
- Academia Sinica 2009 (May 2009 - Taipei, Taiwan) - [Part 1](Pin_Doc/pintutorial-academiasinica-1.ppt) [PPT 469KB] and [Part 2](Pin_Doc/pintutorial-academiasinica-2.ppt) [PPT 299KB]
- ISCA 2008 (June 2008 - Beijing, China) - [Part 1](Pin_Doc/isca2008-pintutorial-partone.ppt) [PPT 469KB] and [Part 2](Pin_Doc/isca2008-pintutorial-parttwo.ppt) [PPT 220KB]
- ASPLOS 2008 (March 2008 - Seattle, WA) - [Slides](Pin_Doc/asplos2008-pintutorial.ppt) [PPT 409KB] and [Hands On](Pin_Doc/asplos2008-handson-256675.pdf) [PDF 365KB] materials
- PLDI 2007 (June 2007 - San Diego, CA) - [Slides](Pin_Doc/pldi2007-pintutorial-256675.pdf) [PDF 5.601MB]

## Related Content

- [GTPin - A Dynamic Binary Instrumentation Framework](Pin_Doc/pldi2007-pintutorial-256675.pdf)
- [Intel® Software Development Emulator]https://software.intel.com/content/www/cn/zh/develop/articles/intel-software-development-emulator.html)
- Pin - A Binary Instrumentation Tool - Downloads[下载链接](https://software.intel.com/content/www/cn/zh/develop/articles/pin-a-binary-instrumentation-tool-downloads.html)
- [Pin - A Binary Instrumentation Tool - FAQ​](https://software.intel.com/content/www/cn/zh/develop/articles/pin-a-binary-instrumentation-tool-faq.html)
- [pinheads@groups.io - Newsgroup](http://groups.io/g/pinheads)
- [Pin - A Binary Instrumentation Tool - Papers](https://software.intel.com/content/www/cn/zh/develop/articles/pin-a-binary-instrumentation-tool-papers.html)
- [Intel® X86 Encoder Decoder Software Library](https://software.intel.com/content/www/cn/zh/develop/articles/xed-x86-encoder-decoder-software-library.html)
- [Pin - A Binary Instrumentation Tool - PinPoints](https://software.intel.com/content/www/cn/zh/develop/articles/pin-a-binary-instrumentation-tool-pinpoints.html)
- [Program Record/Replay Toolkit](https://software.intel.com/content/www/cn/zh/develop/articles/program-recordreplay-toolkit.html)
- [DrDebug: Deterministic Replay based Debugging with Pi](https://software.intel.com/content/www/cn/zh/develop/articles/pintool-drdebug.html)

## Pin 3.18 User Guide

Pin是用于程序检测的工具。它支持IA-32，Intel（R）64和Intel（R）Many Integrated Core体系结构的Linux *，macOS *和Windows *操作系统以及可执行文件。

Pin允许工具在可执行文件中的任意位置插入任意代码（用C或C ++编写）。该代码在可执行文件运行时动态添加。 这也使得可以将Pin附加到已经运行的进程。

Pin提供了一个丰富的API，可以抽象出底层的指令集特性，并允许将诸如寄存器内容之类的上下文信息作为参数传递给注入的代码。 Pin会自动保存和恢复被注入的代码覆盖的寄存器，因此应用程序可以继续工作。 也可以访问符号和调试信息。

Pin包含大量示例检测工具的源代码，例如基本块分析器，高速缓存模拟器，指令跟踪生成器等。使用这些示例作为模板很容易派生新工具。

### How to Instrument with Pin

#### Pin

对Pin的最好的理解是一个“及时”（JIT）编译器。但是，此编译器的输入不是字节码，而是常规可执行文件。 Pin截取可执行文件的第一条指令的执行，并从该指令开始为直线代码序列生成（“编译”）新代码。然后将控制转移到生成的序列。生成的代码序列几乎与原始代码序列相同，但是Pin确保在分支退出序列时重新获得控制。重新获得控制权后，Pin为分支目标生成更多代码并继续执行。Pin通过将所有生成的代码保存在内存中来提高效率，以便可以重用并直接从一个序列分支到另一个序列。

在JIT模式下，曾经执行过的唯一代码是生成的代码。原始代码仅供参考。生成代码时，Pin使用户有机会注入自己的代码（Instrumentation）。

PIN会记录所有实际执行的指令。它们驻留在哪个部分中都没有关系。尽管条件分支有一些例外情况，但通常来说，如果从不执行一条指令，则不会对其进行检测。

#### Pintools

从概念上讲，代码注入包含两个组件：

- 一种决定在何处插入什么代码的机制
- 在插入点执行的代码

这两个组件是检测代码和分析代码。 这两个组件都位于一个可执行文件Pintool中。 Pintools可以看作是可以修改Pin内部代码生成过程的插件。
Pintool会在需要生成新代码的情况下在Pin中注册检测回调例程，该检测回调例程表示检测组件。 它检查要生成的代码，调查其静态属性，并确定是否以及在何处注入对分析函数的调用。
分析功能收集有关应用程序的数据。 PIN确保整数和浮点寄存器的状态在必要时得以保存和恢复，并允许将参数传递给函数。
Pintool还可以为诸如线程创建或派生之类的事件注册通知回调例程。 这些回调通常用于收集数据或工具初始化或清理。

#### Observations

由于Pintool像插件一样工作，因此它必须在与Pin和要检测的可执行文件相同的地址空间中运行。 因此，Pintool可以访问所有可执行文件的数据。 它还与可执行文件共享文件描述符和其他进程信息。
Pin和Pintool从第一条指令开始控制程序。 对于使用共享库编译的可执行文件，这意味着动态加载程序和所有共享库的执行对于Pintool都是可见的。
在编写工具时，调整分析代码比检测代码更重要。 这是因为检测仅执行一次，但是分析代码却被多次调用。

#### Instrumentation Granularity

如上所述，Pin的检测是“及时”（JIT）。在第一次执行代码序列之前立即进行检测。我们将这种操作称为跟踪检测模式。
跟踪检测使Pintool一次可以检查和检测一个可执行文件的跟踪。跟踪通常从采用分支的目标开始，以无条件分支结束，包括调用和返回。 Pin保证仅在顶部输入跟踪，但是它可以包含多个出口。如果分支连接到跟踪的中间，则Pin会构建一个以分支目标开头的新跟踪。Pin将迹线分为基本块BBL。BBL是单入口单出口指令序列。bbl中间的分支开始新的跟踪，并因此开始新的BBL。通常可以为BBL插入一个分析调用，而不是为每个指令插入一个分析调用。减少分析调用的数量可以提高检测效率。 跟踪检测利用TRACE_AddInstrumentFunction API调用。
但是请注意，由于Pin在执行程序时会动态发现程序的控制流，因此Pin的BBL可能不同于在编译器教科书中可以找到的BBL的经典定义。 例如，考虑为switch语句的主体生成的代码，如下所示:
```c++
switch(i)
{
    case 4: total++;
    case 3: total++;
    case 2: total++;
    case 1: total++;
    case 0:
    default: break;
}
```
它将生成类似这样的指令（对于IA-32架构）:
```assemble
.L7:
        addl    $1, -4(%ebp)
.L6:
        addl    $1, -4(%ebp)
.L5:
        addl    $1, -4(%ebp)
.L4:
        addl    $1, -4(%ebp)
```
就经典基本块而言，每个addl指令都在单个指令基本块中。但是，由于执行了不同的switch情况，Pin会生成BBL，当输入.L7情况时，这些BBL包含所有四个指令，当输入.L6情况时，这些BBL包含三个指令，依此类推。这意味着，如果您认为Pin BBL与课本中的基本块相同，那么对引脚BBL进行计数就不太可能得到您期望的计数。例如，在这里，如果代码分支到.L7，则将计为一个Pin BBL，但是执行了四个经典基本块。

Pin还会破坏其他某些可能无法预料的指令上的BBL，例如cpuid，popf和REP前缀的指令会终止所有迹线，因此也会破坏BBL。由于REP前缀指令被视为隐式循环，因此，如果REP前缀指令多次迭代，则在第一个指令之后的迭代将导致生成单个指令BBL，因此在这种情况下，您将看到比预期更多的基本块执行。

为了方便Pintool编写者，Pin还提供了一种指令检测模式，该模式可使工具一次检查和检测可执行文件中的一条指令。这基本上与跟踪工具相同，在该工具中，Pintool编写器已摆脱了对跟踪内部的指令进行迭代的责任。如在跟踪检测中所述，某些BBL及其内部的指令可能会多次生成。指令检测利用INS_AddInstrumentFunction API调用。

但是，有时候，查看与跟踪不同的粒度可能会很有用。为此，Pin提供了两种附加模式：镜像和常规检测。这些模式是通过“缓存”检测请求来实现的，因此会产生空间开销，这些模式也被称为提前检测。

镜像检测使Pintool可以在首次加载时检查并检测整个IMG。Pintool可以遍历映像的部分SEC，部分的例程RTN和例程的指令INS。可以插入工具，以便在执行例程之前或之后或在执行指令之前或之后执行它。镜像检测利用IMG_AddInstrumentFunction API调用。镜像检测取决于符号信息来确定例程边界，因此必须在PIN_Init之前调用PIN_InitSymbols。

例程检测使Pintool在第一次加载包含其映像的图像时检查并检测整个例程。 Pintool可以执行例程的指令。没有足够的信息可用于将指令分解为BBL。可以插入工具，以便在执行例程之前或之后或在执行指令之前或之后执行它。如上一段所述，提供了例行检测程序，以方便Pintool编写者，也可以代替在Image检测程序中遍历映像的各节和例程。

常规检测利用RTN_AddInstrumentFunction API调用。在存在尾部调用或无法可靠地检测到返回指令的情况下，常规出口的检测不能可靠地工作。

请注意，在Image和Routine工具中，不可能知道例程是否会实际执行（因为这些工具是在图像加载时完成的）。通过标识作为例程开始的指令，可以仅遍历在Trace或Instruction工具例程中执行的例程的指令。请参阅工具Tests/parse_executed_rtns.cpp。

#### Managed platforms support

#### Symbols

#### Floating Point Support in Analysis Routines

#### Instrumenting Multi-threaded Applications

#### Avoiding Deadlocks in Multi-threaded Applications



### Examples

#### Building the Example Tools

- 构建文件夹中所有例子(ia32架构)
```bash
cd source/tools/ManualExamples
make all TARGET=Intel64
```

- 构建文件夹中所有例子(Intel64架构)
```bash
$ cd source/tools/ManualExamples
$ make all TARGET=intel64
```

- 构建并运行某一例子
```bash
$ cd source/tools/ManualExamples
$ make inscount0.test TARGET=intel64
```

- 构建但不运行某一例子
```bash
$ cd source/tools/ManualExamples
$ make obj-intel64/inscount0.test TARGET=intel64
```

#### Simple Instruction Count (Instruction Instrumentation)

下面的示例对一个程序进行计数，以计算所执行指令的总数。它在每条指令之前插入一个对docount的调用。 程序退出时，它将计数保存在文件inscount.out中。
```bash
$ ../../../pin -t obj-intel64/inscount0.so -- /bin/ls
$ cat inscount.out
Count 422838
```

如果需要指定输出文件，使用"-o <file_name>"，但是需要插入到工具名称和双虚线(--)之间。
```bash
$ ../../../pin -t obj-intel64/inscount0.so -o inscount0.log -- /bin/ls
```

该示例可以在source/tools/ManualExamples/inscount0.cpp中找到：
```c
#include <iostream>
#include <fstream>
#include "pin.H"
using std::cerr;
using std::ofstream;
using std::ios;
using std::string;
using std::endl;
 
ofstream OutFile;
 
// The running count of instructions is kept here
// make it static to help the compiler optimize docount
static UINT64 icount = 0;
 
// This function is called before every instruction is executed
VOID docount() { icount++; }
    
// Pin calls this function every time a new instruction is encountered
VOID Instruction(INS ins, VOID *v)
{
    // Insert a call to docount before every instruction, no arguments are passed
    INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)docount, IARG_END);
}
 
KNOB<string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool",
    "o", "inscount.out", "specify output file name");
 
// This function is called when the application exits
VOID Fini(INT32 code, VOID *v)
{
    // Write to a file since cout and cerr maybe closed by the application
    OutFile.setf(ios::showbase);
    OutFile << "Count " << icount << endl;
    OutFile.close();
}
 
/* ===================================================================== */
/* Print Help Message                                                    */
/* ===================================================================== */
 
INT32 Usage()
{
    cerr << "This tool counts the number of dynamic instructions executed" << endl;
    cerr << endl << KNOB_BASE::StringKnobSummary() << endl;
    return -1;
}
 
/* ===================================================================== */
/* Main                                                                  */
/* ===================================================================== */
/*   argc, argv are the entire command line: pin -t <toolname> -- ...    */
/* ===================================================================== */
 
int main(int argc, char * argv[])
{
    // Initialize pin
    if (PIN_Init(argc, argv)) return Usage();
 
    OutFile.open(KnobOutputFile.Value().c_str());
 
    // Register Instruction to be called to instrument instructions
    INS_AddInstrumentFunction(Instruction, 0);
 
    // Register Fini to be called when the application exits
    PIN_AddFiniFunction(Fini, 0);
    
    // Start the program, never returns
    PIN_StartProgram();
    
    return 0;
}
```

#### Instruction Address Trace (Instruction Instrumentation)

在前面的示例中，我们没有将任何参数传递给分析过程docount。 在这个例子中，我们展示了如何传递参数。 调用分析过程时，Pin允许您传递指令指针，寄存器的当前值，存储器操作的有效地址，常量等。有关完整列表，请参见[IARG_TYPE](https://software.intel.com/sites/landingpage/pintool/docs/98332/Pin/html/group__INST__ARGS.html#ga089c27ca15e9ff139dd3a3f8a6f8451d)。

稍作更改，我们就可以将指令计数示例转换为Pintool，该Pintool将打印每条执行的指令的地址。该工具对于了解用于调试的程序的控制流或在模拟指令高速缓存时的处理器设计中很有用。

我们将参数更改为INS_InsertCall，以传递将要执行的指令的地址。我们用printip代替docount，它会打印指令地址。它将其输出写入文件itrace.out。
```bash
$ ../../../pin -t obj-intel64/itrace.so -- /bin/ls
Makefile          atrace.o     imageload.out  itrace      proccount
Makefile.example  imageload    inscount0      itrace.o    proccount.o
atrace            imageload.o  inscount0.o    itrace.out
$ head itrace.out
0x40001e90
0x40001e91
0x40001ee4
0x40001ee5
0x40001ee7
0x40001ee8
0x40001ee9
0x40001eea
0x40001ef0
0x40001ee0
```

该示例可以在source/tools/ManualExamples/itrace.cpp中找到：
```c
#include <stdio.h>
#include "pin.H"
 
FILE * trace;
 
// This function is called before every instruction is executed
// and prints the IP
VOID printip(VOID *ip) { fprintf(trace, "%p\n", ip); }
 
// Pin calls this function every time a new instruction is encountered
VOID Instruction(INS ins, VOID *v)
{
    // Insert a call to printip before every instruction, and pass it the IP
    INS_InsertCall(ins, IPOINT_BEFORE, (AFUNPTR)printip, IARG_INST_PTR, IARG_END);
}
 
// This function is called when the application exits
VOID Fini(INT32 code, VOID *v)
{
    fprintf(trace, "#eof\n");
    fclose(trace);
}
 
/* ===================================================================== */
/* Print Help Message                                                    */
/* ===================================================================== */
 
INT32 Usage()
{
    PIN_ERROR("This Pintool prints the IPs of every instruction executed\n" 
              + KNOB_BASE::StringKnobSummary() + "\n");
    return -1;
}
 
/* ===================================================================== */
/* Main                                                                  */
/* ===================================================================== */
 
int main(int argc, char * argv[])
{
    trace = fopen("itrace.out", "w");
    
    // Initialize pin
    if (PIN_Init(argc, argv)) return Usage();
 
    // Register Instruction to be called to instrument instructions
    INS_AddInstrumentFunction(Instruction, 0);
 
    // Register Fini to be called when the application exits
    PIN_AddFiniFunction(Fini, 0);
    
    // Start the program, never returns
    PIN_StartProgram();
    
    return 0;
}
```

#### Memory Reference Trace (Instruction Instrumentation)

前面的示例将检测所有指令。有时工具可能只想检测一类指令，例如内存操作或分支指令。工具可以通过使用Pin API来做到这一点，Pin API包括对指令进行分类和检查的功能。基本API对所有指令集都是通用的，[在此]()进行描述。此外，还有针对[IA-32 ISA](https://software.intel.com/sites/landingpage/pintool/docs/98332/Pin/html/group__INS__BASIC__API__IA32.html)的指令集特定的API。

在这个例子中，我们展示了如何通过检查指令来做更多的选择性检测。该工具生成程序引用的所有内存地址的跟踪。这对于调试和模拟处理器中的数据缓存也很有用。

我们仅检测读或写内存的指令。我们还使用INS_InsertPredicatedCall而不是INS_InsertCall来避免在断言为false时生成对断言指令的引用。在IA-32和Intel®64体系结构上，将CMOVcc，FCMOVcc和REP前缀字符串操作视为断言。对于CMOVcc和FCMOVcc，该谓词是“ cc”所隐含的条件测试，对于REP带有前缀的字符串ops，则是计数寄存器为非零。

由于每次执行一条指令时仅调用一次检测功能，而调用一次分析功能，因此与仅对内存操作进行检测相比，仅对内存操作进行检测要快得多。

这是运行它的方法和示例输出：

```bash
$ ../../../pin -t obj-intel64/pinatrace.so -- /bin/ls
Makefile          atrace.o    imageload.o    inscount0.o  itrace.out
Makefile.example  atrace.out  imageload.out  itrace       proccount
atrace            imageload   inscount0      itrace.o     proccount.o
$ head pinatrace.out
0x40001ee0: R 0xbfffe798
0x40001efd: W 0xbfffe7d4
0x40001f09: W 0xbfffe7d8
0x40001f20: W 0xbfffe864
0x40001f20: W 0xbfffe868
0x40001f20: W 0xbfffe86c
0x40001f20: W 0xbfffe870
0x40001f20: W 0xbfffe874
0x40001f20: W 0xbfffe878
0x40001f20: W 0xbfffe87c
```

该示例可以在source/tools/ManualExamples/pinatrace.cpp中找到

```c
/*
 *  This file contains an ISA-portable PIN tool for tracing memory accesses.
 */
 
#include <stdio.h>
#include "pin.H"
 
 
FILE * trace;
 
// Print a memory read record
VOID RecordMemRead(VOID * ip, VOID * addr)
{
    fprintf(trace,"%p: R %p\n", ip, addr);
}
 
// Print a memory write record
VOID RecordMemWrite(VOID * ip, VOID * addr)
{
    fprintf(trace,"%p: W %p\n", ip, addr);
}
 
// Is called for every instruction and instruments reads and writes
VOID Instruction(INS ins, VOID *v)
{
    // Instruments memory accesses using a predicated call, i.e.
    // the instrumentation is called iff the instruction will actually be executed.
    //
    // On the IA-32 and Intel(R) 64 architectures conditional moves and REP 
    // prefixed instructions appear as predicated instructions in Pin.
    UINT32 memOperands = INS_MemoryOperandCount(ins);
 
    // Iterate over each memory operand of the instruction.
    for (UINT32 memOp = 0; memOp < memOperands; memOp++)
    {
        if (INS_MemoryOperandIsRead(ins, memOp))
        {
            INS_InsertPredicatedCall(
                ins, IPOINT_BEFORE, (AFUNPTR)RecordMemRead,
                IARG_INST_PTR,
                IARG_MEMORYOP_EA, memOp,
                IARG_END);
        }
        // Note that in some architectures a single memory operand can be 
        // both read and written (for instance incl (%eax) on IA-32)
        // In that case we instrument it once for read and once for write.
        if (INS_MemoryOperandIsWritten(ins, memOp))
        {
            INS_InsertPredicatedCall(
                ins, IPOINT_BEFORE, (AFUNPTR)RecordMemWrite,
                IARG_INST_PTR,
                IARG_MEMORYOP_EA, memOp,
                IARG_END);
        }
    }
}
 
VOID Fini(INT32 code, VOID *v)
{
    fprintf(trace, "#eof\n");
    fclose(trace);
}
 
/* ===================================================================== */
/* Print Help Message                                                    */
/* ===================================================================== */
   
INT32 Usage()
{
    PIN_ERROR( "This Pintool prints a trace of memory addresses\n" 
              + KNOB_BASE::StringKnobSummary() + "\n");
    return -1;
}
 
/* ===================================================================== */
/* Main                                                                  */
/* ===================================================================== */
 
int main(int argc, char *argv[])
{
    if (PIN_Init(argc, argv)) return Usage();
 
    trace = fopen("pinatrace.out", "w");
 
    INS_AddInstrumentFunction(Instruction, 0);
    PIN_AddFiniFunction(Fini, 0);
 
    // Never returns
    PIN_StartProgram();
    
    return 0;
}
```




#### Detecting the Loading and Unloading of Images (Image Instrumentation)
#### More Efficient Instruction Counting (Trace Instrumentation)
#### Procedure Instruction Count (Routine Instrumentation)
#### Using PIN_SafeCopy()
#### Order of Instrumentation
#### Finding the Value of Function Arguments
#### Finding Functions By Name on Windows
#### Instrumenting Threaded Applications
#### Using TLS
#### Using the Fast Buffering APIs
#### Finding the Static Properties of an Image
#### Detaching Pin from the Application
#### Replacing a Routine in Probe Mode
#### Instrumenting Child Processes
#### Instrumenting Before and After Forks
#### Managed platforms support


### Callbacks

### Modifying Application Instructions
### The Pin Advanced Debugging Extensions
### Applying a Pintool to an Application
### Tips for Debugging a Pintool
### Logging Messages from a Pintool
### Performance Considerations
### Memory management
### PinTools Information and Restrictions
### Building Tools on windows
### Libraries for Windows
### Libraries for Linux
### Installation
### Building Your Own Tool
### Pin's makefile Infrastructure
### Feedback
### Disclaimer and Legal Information
### Pin API reference
### Pin Command Line Switches
### Instrumentation Library