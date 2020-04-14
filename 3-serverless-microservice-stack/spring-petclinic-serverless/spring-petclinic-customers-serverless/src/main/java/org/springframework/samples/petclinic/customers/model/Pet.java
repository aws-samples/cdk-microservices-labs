/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: MIT-0
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this
 * software and associated documentation files (the "Software"), to deal in the Software
 * without restriction, including without limitation the rights to use, copy, modify,
 * merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
 * INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
 * PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 * HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 * OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

package org.springframework.samples.petclinic.customers.model;

import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBDocument;
import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBGeneratedUuid;
import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBAutoGenerateStrategy;

import java.util.Date;
import java.util.UUID;

@DynamoDBDocument
public class Pet {

        private int id;
        private String name;
        private Date birthDate;
        private String type;
        
        public Pet(String name, Date birthDate, String type){
            this.name = name;
            this.birthDate = birthDate;
            this.type = type;
        }
        
        public Pet(){
            
        }
        
        
        public int getId() {
            return id;
        }
    
        public void setId(final int id) {
            this.id = id;
        }
    
        public String getName() {
            return this.name;
        }
    
        public void setName(final String name) {
            this.name = name;
        }
    
        public Date getBirthDate() {
            return birthDate;
        }
    
        public void setBirthDate(final Date birthDate) {
            this.birthDate = birthDate;
        }
        
        public String getType(){
            return type;
        }
        
        public void setType(String type){
            this.type = type;
        }
    
    }