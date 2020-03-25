/*
 * Copyright 2002-2017 the original author or authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.springframework.samples.petclinic.vets;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;
import org.springframework.boot.autoconfigure.jdbc.DataSourceTransactionManagerAutoConfiguration;
import org.springframework.boot.autoconfigure.orm.jpa.HibernateJpaAutoConfiguration;
import org.socialsignin.spring.data.dynamodb.repository.config.EnableDynamoDBRepositories;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.samples.petclinic.vets.model.Vet;
import org.springframework.samples.petclinic.vets.model.VetRepository;
import org.springframework.samples.petclinic.vets.common.DynamoDBConfig;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.context.annotation.Bean;
import org.springframework.boot.CommandLineRunner;

import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBMapper;
import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBMapperConfig;
import com.amazonaws.services.dynamodbv2.model.CreateTableRequest;
import com.amazonaws.services.dynamodbv2.model.ProvisionedThroughput;
import com.amazonaws.services.dynamodbv2.util.TableUtils;

import java.util.Set;
import java.util.HashSet;


@EnableAutoConfiguration(exclude = {DataSourceAutoConfiguration.class, // No JPA
		DataSourceTransactionManagerAutoConfiguration.class, HibernateJpaAutoConfiguration.class})
@EnableDynamoDBRepositories(mappingContextRef = "dynamoDBMappingContext",
                            dynamoDBMapperConfigRef = "dynamoDBMapperConfig",
                            basePackageClasses = VetRepository.class)
@Configuration
@Import({DynamoDBConfig.class})

@SpringBootApplication
public class VetsServiceApplication {

	public static void main(String[] args) {
		SpringApplication.run(VetsServiceApplication.class, args);
	}
	
	// @Bean
	// public CommandLineRunner init(ConfigurableApplicationContext ctx, VetRepository dynamoDBRepository,
	// 		 AmazonDynamoDB amazonDynamoDB, DynamoDBMapper dynamoDBMapper, DynamoDBMapperConfig config) {
	// 	return (args) -> {

	// 		CreateTableRequest ctr = dynamoDBMapper.generateCreateTableRequest(Vet.class)
	// 				.withProvisionedThroughput(new ProvisionedThroughput(5L, 5L));
	// 		boolean created =TableUtils.createTableIfNotExists(amazonDynamoDB, ctr);
	// 		if (created) {
	// 		    TableUtils.waitUntilActive(amazonDynamoDB, ctr.getTableName());
	// 		    createEntities(dynamoDBRepository);
	// 		}
	// 	};
	// }
	
	// private void createEntities(VetRepository dynamoDBRepository) {
	// 	// save a couple of devices

 //       Set hs1 = new HashSet();
	// 	Set hs2 = new HashSet();
	// 	Set hs3 = new HashSet();
	// 	Set hs4 = new HashSet();
	// 	Set hs5 = new HashSet();
	// 	Set hs6 = new HashSet();
		
	// 	hs1.add("dentistry");
	// 	hs2.add("radiology");
	// 	hs3.add("surgery");
	// 	hs3.add("dentistry");
	// 	hs4.add("surgery");
	// 	hs5.add("radiology");
	// 	hs6.add("surgery");
		
	// 	dynamoDBRepository.save(new Vet("James", "Carter", hs1));
	// 	dynamoDBRepository.save(new Vet("Helen", "Leary", hs2));
	// 	dynamoDBRepository.save(new Vet("Linda", "Douglas", hs3));
	// 	dynamoDBRepository.save(new Vet("Rafael", "Ortega", hs4));
	// 	dynamoDBRepository.save(new Vet("Henry", "Stevens", hs5));
	// 	dynamoDBRepository.save(new Vet("Sharon", "Jenkins", hs6));
		
	// }
}
