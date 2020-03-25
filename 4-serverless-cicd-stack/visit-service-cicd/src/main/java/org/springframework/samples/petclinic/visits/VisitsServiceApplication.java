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
package org.springframework.samples.petclinic.visits;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration;
import org.springframework.boot.autoconfigure.jdbc.DataSourceTransactionManagerAutoConfiguration;
import org.springframework.boot.autoconfigure.orm.jpa.HibernateJpaAutoConfiguration;
import org.socialsignin.spring.data.dynamodb.repository.config.EnableDynamoDBRepositories;
import org.springframework.boot.autoconfigure.EnableAutoConfiguration;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Import;
import org.springframework.samples.petclinic.visits.model.Visit;
import org.springframework.samples.petclinic.visits.model.VisitRepository;
import org.springframework.samples.petclinic.visits.common.DynamoDBConfig;
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
import java.util.Date;

@EnableAutoConfiguration(exclude = {DataSourceAutoConfiguration.class, // No JPA
		DataSourceTransactionManagerAutoConfiguration.class, HibernateJpaAutoConfiguration.class})
@EnableDynamoDBRepositories(mappingContextRef = "dynamoDBMappingContext",
                            dynamoDBMapperConfigRef = "dynamoDBMapperConfig",
                            basePackageClasses = VisitRepository.class)
@Configuration
@Import({DynamoDBConfig.class})
@SpringBootApplication
public class VisitsServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(VisitsServiceApplication.class, args);
    }
    
 //   @Bean
	// public CommandLineRunner init(ConfigurableApplicationContext ctx, VisitRepository dynamoDBRepository,
	// 		AmazonDynamoDB amazonDynamoDB, DynamoDBMapper dynamoDBMapper, DynamoDBMapperConfig config) {
	// 	return (args) -> {

	// 		CreateTableRequest ctr = dynamoDBMapper.generateCreateTableRequest(Visit.class)
	// 				.withProvisionedThroughput(new ProvisionedThroughput(5L, 5L));
	// 		boolean created =TableUtils.createTableIfNotExists(amazonDynamoDB, ctr);
	// 		if (created) {
	// 		    TableUtils.waitUntilActive(amazonDynamoDB, ctr.getTableName());
	// 		    createEntities(dynamoDBRepository);
	// 		}
	// 	};
	// }
	
	// private void createEntities(VisitRepository dynamoDBRepository) {
	//     dynamoDBRepository.save(new Visit("1edd8520-ddfe-44f4-80cb-9665202bef6b","Mulligan", new Date()));
	//     dynamoDBRepository.save(new Visit("5f47ea2b-c8eb-49c5-8489-b87869a94fc8","Leo", new Date()));
	// }
}
