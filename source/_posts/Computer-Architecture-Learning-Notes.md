---
title: Computer_Architecture_Learning_Notes
date: 2021-06-02 22:25:07
tags: 计算机体系结构
description: CA学习笔记
categories: 技术博客
---

## 术语解释

**1. [Interleaved memory](https://en.wikipedia.org/wiki/Interleaved_memory)**

![](BlogFig/Interleaving.gif)

In computing, interleaved memory is a design which compensates for the relatively slow speed of DRAM or core memory, by spreading memory addresses evenly across memory banks. That way, contiguous memory reads and writes use each memory bank in turn, resulting in higher memory throughout due to reduced waiting for memory banks to become ready for the operations.

It is different from multi-channel memory architectures, primarily as interleaved memory does not add more channels between the main memory and the memory controller. However, channel interleaving is also possible, for example in freescale i.MX6 processors, which allow interleaving to be done between two channels.


<!-- $\begin{bmatrix}
{X_1}\\
{X_2}\\
{\vdots}\\
{X_n}\\
\end{bmatrix} = 
\begin{bmatrix}
{W_1^1}&{W_1^2}&{\cdots}&{W_1^n}\\
{W_2^1}&{W_2^2}&{\cdots}&{W_2^n}\\
{\vdots}&{\vdots}&{\ddots}&{\vdots}\\
{W_n^1}&{W_n^2}&{\cdots}&{W_n^n}\\
\end{bmatrix} 
\begin{bmatrix}
{x_1}\\
{x_2}\\
{\vdots}\\
{x_n}\\
\end{bmatrix}$

| R($W_1^1$) 	| I($W_1^2$) 	| R($W_1^2$) 	| I($W_1^2$) 	| ... 	| R($W_1^n$) 	| I($W_1^n$) 	|
|:----:	|:----:	|:----:	|:----:	|:---:	|:----:	|:----:	|
| -I($W_1^1$) 	| R($W_1^2$) 	| -I($W_1^2$) 	| R($W_1^2$) 	| ... 	| -I($W_1^n$) 	| R($W_1^n$) 	|
| R($W_2^1$) 	| I($W_2^2$) 	| R($W_2^2$) 	| I($W_2^2$) 	| ... 	| R($W_2^n$) 	| I($W_2^n$) 	|
| -I($W_2^1$) 	| R($W_2^2$) 	| -I($W_2^2$) 	| R($W_2^2$) 	| ... 	| -I($W_2^n$) 	| R($W_2^n$) 	|
|  ... 	|  ... 	|  ... 	|  ... 	| ... 	|  ... 	|  ... 	|
| R($W_n^1$) 	| I($W_n^2$) 	| R($W_n^2$) 	| I($W_n^2$) 	| ... 	| R($W_n^n$) 	| I($W_n^n$) 	|
| -I($W_n^1$) 	| R($W_n^2$) 	| -I($W_n^2$) 	| R($W_n^2$) 	| ... 	| -I($W_n^n$) 	| R($W_n^n$) 	| -->