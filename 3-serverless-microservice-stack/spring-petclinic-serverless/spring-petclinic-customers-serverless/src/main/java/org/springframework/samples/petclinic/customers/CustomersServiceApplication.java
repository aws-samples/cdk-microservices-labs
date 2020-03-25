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
 
package org.springframework.samples.petclinic.customers;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;
import org.springframework.boot.autoconfigure.jdbc.DataSourceTransactionManagerAutoConfiguration;
import org.springframework.boot.autoconfigure.orm.jpa.HibernateJpaAutoConfiguration;
import org.socialsignin.spring.data.dynamodb.repository.config.EnableDynamoDBRepositories;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.samples.petclinic.customers.model.Owner;
import org.springframework.samples.petclinic.customers.model.Pet;
import org.springframework.samples.petclinic.customers.model.OwnerRepository;
import org.springframework.samples.petclinic.customers.common.DynamoDBConfig;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.context.annotation.Bean;

import org.springframework.boot.CommandLineRunner;

import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBMapper;
import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBMapperConfig;
import com.amazonaws.services.dynamodbv2.model.CreateTableRequest;
import com.amazonaws.services.dynamodbv2.model.ProvisionedThroughput;
import com.amazonaws.services.dynamodbv2.util.TableUtils;

import java.util.ArrayList;
import java.util.List;
import java.util.Date;
import java.text.SimpleDateFormat;
import java.time.Instant;
import java.time.Duration;

import lombok.extern.slf4j.Slf4j;

@EnableAutoConfiguration(exclude = {DataSourceAutoConfiguration.class, // No JPA
		DataSourceTransactionManagerAutoConfiguration.class, HibernateJpaAutoConfiguration.class})
@EnableDynamoDBRepositories(mappingContextRef = "dynamoDBMappingContext",
                            dynamoDBMapperConfigRef = "dynamoDBMapperConfig",
                            basePackageClasses = OwnerRepository.class)
@Configuration
@Import({DynamoDBConfig.class})
@SpringBootApplication
@Slf4j
public class CustomersServiceApplication {

	public static void main(String[] args) {
		SpringApplication.run(CustomersServiceApplication.class, args);
	}
	
// 	@Bean
// 	public CommandLineRunner init(ConfigurableApplicationContext ctx, OwnerRepository dynamoDBRepository,
// 			AmazonDynamoDB amazonDynamoDB, DynamoDBMapper dynamoDBMapper, DynamoDBMapperConfig config) {
// 		return (args) -> {

//             Instant start = Instant.now();
// 			CreateTableRequest ctr = dynamoDBMapper.generateCreateTableRequest(Owner.class)
// 					.withProvisionedThroughput(new ProvisionedThroughput(5L, 5L));
// 			boolean created = TableUtils.createTableIfNotExists(amazonDynamoDB, ctr);
// 			if (created) {
// 			    log.info("Table not exists!");
// 			    TableUtils.waitUntilActive(amazonDynamoDB, ctr.getTableName());
// 			    createEntities(dynamoDBRepository);
// 			}else{
// 			    log.info("Table exists!!");
// 			}
// 			Instant finish = Instant.now();
// 			long timeElapsed = Duration.between(start, finish).toMillis();
// 			log.info("Init for DynamoDB table and data elapse for: " + timeElapsed + "ms.");
// 		};
// 	}
	
// 	private void createEntities(OwnerRepository dynamoDBRepository) {
// 		// save a couple of devices

//         SimpleDateFormat ft = new SimpleDateFormat ("yyyy-MM-dd");
        
//         List<Pet> pets1 = new ArrayList<>();
//         List<Pet> pets2 = new ArrayList<>();
//         List<Pet> pets3 = new ArrayList<>();
//         List<Pet> pets4 = new ArrayList<>();
//         List<Pet> pets5 = new ArrayList<>();
//         List<Pet> pets6 = new ArrayList<>();
//         List<Pet> pets7 = new ArrayList<>();
//         List<Pet> pets8 = new ArrayList<>();
//         List<Pet> pets9 = new ArrayList<>();
//         List<Pet> pets10 = new ArrayList<>();
//         List<Pet> pets11 = new ArrayList<>();
        
        
//         try{
//             pets1.add(new Pet("Leo", ft.parse("2000-09-07"), "cat"));
//             pets2.add(new Pet("Basil", ft.parse("2002-08-06"), "hamster"));
//             pets3.add(new Pet("Rosy", ft.parse("2001-04-17"), "dog"));
//             pets3.add(new Pet("Jewel", ft.parse("2000-03-07"), "dog"));
//             pets4.add(new Pet("Iggy", ft.parse("2000-11-30"), "lizard"));
//             pets5.add(new Pet("George", ft.parse("2000-01-20"), "snake"));
//             pets6.add(new Pet("Samantha", ft.parse("1995-09-04"), "cat"));
//             pets6.add(new Pet("Max", ft.parse("1995-09-04"), "cat"));
//             pets7.add(new Pet("Lucky", ft.parse("1999-08-06"), "bird"));
//             pets8.add(new Pet("Mulligan", ft.parse("1997-02-24"), "dog"));
//             pets9.add(new Pet("Freddy", ft.parse("2000-03-09"), "bird"));
//             pets10.add(new Pet("Lucky", ft.parse("2000-06-24"), "dog"));
//             pets10.add(new Pet("Sly", ft.parse("2002-06-08"), "cat"));
    		
//     		dynamoDBRepository.save(new Owner("George", "Franklin", "110 W. Liberty St.", "Madison", "6085551023", pets1));
//     		dynamoDBRepository.save(new Owner("Betty", "Davis", "638 Cardinal Ave.", "Sun Prairie", "6085551749", pets2));
//     		dynamoDBRepository.save(new Owner("Eduardo", "Rodriquez", "2693 Commerce St.", "McFarland", "6085558763", pets3));
//     		dynamoDBRepository.save(new Owner("Harold", "Davis", "563 Friendly St.", "Windsor", "6085553198", pets4));
//     		dynamoDBRepository.save(new Owner("Peter", "McTavish", "2387 S. Fair Way", "Madison", "6085552765", pets5));
//     		dynamoDBRepository.save(new Owner("Jean", "Coleman", "105 N. Lake St.", "Monona", "6085552654", pets6));
//     		dynamoDBRepository.save(new Owner("Jeff", "Black", "1450 Oak Blvd.", "Monona", "6085555387", pets7));
//     		dynamoDBRepository.save(new Owner("Maria", "Escobito", "345 Maple St.", "Madison", "6085557683", pets8));
//     		dynamoDBRepository.save(new Owner("David", "Schroeder", "2749 Blackhawk Trail", "Madison", "6085559435", pets9));
//     		dynamoDBRepository.save(new Owner("Carlos", "Estaban", "2335 Independence La.", "Waunakee", "6085555487", pets10));
//     		dynamoDBRepository.save(new Owner("Greg", "Huang", "2335 Independence La.", "Waunakee", "6085555487", pets11));
//         }
//         catch(Exception e){
            
//         }

// 	}
}
