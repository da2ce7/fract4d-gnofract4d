#!/bin/sh
/usr/bin/time -f "%Uuser %Ssystem %Eelapsed %PCPU (%Xtext+%Ddata %Mmax)k" ./gnofract4d -p paramfiles/param.fct -q
