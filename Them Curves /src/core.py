#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 19:50:41 2017

@author: chinmay
"""

import numpy as np

num_features = 2
Learning_rate = 10 ** -3
correction = 0
error_diff_threshold = 0

def adjust_globals(features = 2, Learn_rate = 0.001, correction_factor = 0, error_diff = 0):
    global num_features
    global Learning_rate
    global correction 
    global error_diff_threshold
    num_features = features
    Learning_rate = Learn_rate
    correction = correction_factor
    error_diff_threshold = error_diff

def get_points( infile ):
    '''
    enter .points file to read points.
    
    important guidelines :
        the .points file must contain points in the form x,y on each line without space
        and each line must terminate with a newline character including the last line.
    '''
    if not infile.endswith('.points'):
        raise Exception('file codec is invalid')
    global num_features
    fptr = open( infile, 'r')
    lines = fptr.readlines()
    pointlist = []
    
    for line in lines:     
        pointlist.append( [float(u) for u in line[:len(line) - 1].split(',')] )
    
    pointlist = np.array(pointlist)
    x_vec = pointlist[:,0]
    y_vec = pointlist[:,1]
    feat_vec = [np.zeros(len(pointlist)) + 1]
    del pointlist
    
    for ctr in range(num_features):
        feat_vec.append(x_vec * feat_vec[ctr])
    
    return (np.array(feat_vec), y_vec)

def cost_function(cost_array, hypothesis, y_array):
    '''
    J* = Sigma{(H(x) - Y) ^ 2} + Correction * Sum_all_terms{H} / 2m
    '''
    global correction
    return (np.dot(cost_array,cost_array) + np.dot(hypothesis, hypothesis) * correction) / (2 * len(y_array))
    

def Stepper(x_array, y_array,hypothesis,current_error):
    global Learning_rate
    global correction
    global error_diff_threshold
    
    temp1 = np.subtract( np.dot(hypothesis, x_array), y_array)
    temp2 = hypothesis * (1 - (Learning_rate * correction)/(len(y_array))) 
    new_hypothesis = np.subtract(temp2, np.dot( x_array, temp1) * Learning_rate/ len(y_array))
    
    temp1 = np.subtract( np.dot(new_hypothesis, x_array), y_array)
    new_error = cost_function(temp1, new_hypothesis, y_array)
    
    if current_error - new_error <= error_diff_threshold:
        return False, hypothesis, current_error
    else:
        return True, new_hypothesis, new_error
    
def iterator( x_array, y_array):
    '''
    generates extra polynomial features of x 10 features to be precise 
    and trys fitting them to the data. 
    
    prevents overfitting by using a weight term for theta vector in the 
    cost function.
    '''
    global num_features
    hypothesis = np.zeros(num_features + 1) 
    error = cost_function(y_array, hypothesis,y_array)
    state = True
    
    while(state):
        state, hypothesis, error = Stepper(x_array, y_array,hypothesis,error)
    
    return hypothesis

def fitter( infile ):
    try:
        x, y = get_points(infile)
        print iterator(x, y)
    except:
        print "an unknown error occured, Check file type entered"