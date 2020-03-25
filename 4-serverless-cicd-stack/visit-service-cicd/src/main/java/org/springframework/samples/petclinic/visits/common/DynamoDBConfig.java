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
package org.springframework.samples.petclinic.visits.common;

import org.socialsignin.spring.data.dynamodb.mapping.DynamoDBMappingContext;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Profile;
import org.springframework.beans.factory.annotation.Value;

import com.amazonaws.auth.AWSCredentials;
import com.amazonaws.auth.AWSCredentialsProvider;
import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDB;
import com.amazonaws.services.dynamodbv2.AmazonDynamoDBClientBuilder;
import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBMapper;
import com.amazonaws.services.dynamodbv2.datamodeling.DynamoDBMapperConfig;

@Configuration
public class DynamoDBConfig {

	// @Value("${amazon.aws.accesskey}")
	// private String amazonAWSAccessKey;

	// @Value("${amazon.aws.secretkey}")
	// private String amazonAWSSecretKey;

	// public AWSCredentialsProvider amazonAWSCredentialsProvider() {
	// 	return new AWSStaticCredentialsProvider(amazonAWSCredentials());
	// }

	// @Bean
	// public AWSCredentials amazonAWSCredentials() {
	// 	return new BasicAWSCredentials(amazonAWSAccessKey, amazonAWSSecretKey);
	// }
	
	@Value("${DYNAMODB_TABLE_NAME:VISIT}")
    private String singleTableName;

	@Bean
	public DynamoDBMapperConfig dynamoDBMapperConfig() {
	 	DynamoDBMapperConfig.Builder builder = new DynamoDBMapperConfig.Builder();
		builder.setTableNameOverride(DynamoDBMapperConfig.TableNameOverride.withTableNameReplacement(singleTableName));
	 	
	 	return builder.build();
	}

	@Bean
	public DynamoDBMapper dynamoDBMapper(AmazonDynamoDB amazonDynamoDB, DynamoDBMapperConfig config) {
		return new DynamoDBMapper(amazonDynamoDB, config);
	}

	@Bean
	public AmazonDynamoDB amazonDynamoDB() {
		return AmazonDynamoDBClientBuilder.standard().build();
	}

	@Bean
	public DynamoDBMappingContext dynamoDBMappingContext() {
		return new DynamoDBMappingContext();
	}

}