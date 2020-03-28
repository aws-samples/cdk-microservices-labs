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