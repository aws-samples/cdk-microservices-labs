#! /bin/bash
#Copy the Spring Open Source to build folder
mkdir work/build
cp -r spring-petclinic-microservices/spring-petclinic-api-gateway work/build/spring-petclinic-static-service
cp -r spring-petclinic-microservices/spring-petclinic-customers-service work/build/
cp -r spring-petclinic-microservices/spring-petclinic-vets-service work/build/
cp -r spring-petclinic-microservices/spring-petclinic-visits-service work/build/

cp -r spring-petclinic-microservices/.mvn work/build/
cp spring-petclinic-microservices/mvnw work/build/

# Use our own POM and Properties file
find work/build/spring-petclinic-static-service/src/main/resources/ -maxdepth 1 -type f -delete
find work/build/spring-petclinic-customers-service/src/main/resources/ -maxdepth 1 -type f -delete
find work/build/spring-petclinic-vets-service/src/main/resources/ -maxdepth 1 -type f -delete
find work/build/spring-petclinic-visits-service/src/main/resources/ -maxdepth 1 -type f -delete

cp work/source/*.properties work/build/spring-petclinic-static-service/src/main/resources/
cp work/source/*.properties work/build/spring-petclinic-customers-service/src/main/resources/
cp work/source/*.properties work/build/spring-petclinic-vets-service/src/main/resources/
cp work/source/*.properties work/build/spring-petclinic-visits-service/src/main/resources/

cp work/source/logback-spring.xml work/build/spring-petclinic-static-service/src/main/resources/
cp work/source/logback-spring.xml work/build/spring-petclinic-customers-service/src/main/resources/
cp work/source/logback-spring.xml work/build/spring-petclinic-vets-service/src/main/resources/
cp work/source/logback-spring.xml work/build/spring-petclinic-visits-service/src/main/resources/

cp work/source/Dockerfile work/build/spring-petclinic-static-service/
cp work/source/Dockerfile work/build/spring-petclinic-customers-service/
cp work/source/Dockerfile work/build/spring-petclinic-vets-service/
cp work/source/Dockerfile work/build/spring-petclinic-visits-service/

cp work/source/root_pom.xml work/build/pom.xml

cp work/source/static_pom.xml  work/build/spring-petclinic-static-service/pom.xml
cp work/source/customers_pom.xml  work/build/spring-petclinic-customers-service/pom.xml
cp work/source/vets_pom.xml  work/build/spring-petclinic-vets-service/pom.xml
cp work/source/visits_pom.xml  work/build/spring-petclinic-visits-service/pom.xml

# Copy Modify Source code to build folder
cp work/source/code/ApiGatewayApplication.java work/build/spring-petclinic-static-service/src/main/java/org/springframework/samples/petclinic/api/
cp work/source/code/CustomersServiceApplication.java work/build/spring-petclinic-customers-service/src/main/java/org/springframework/samples/petclinic/customers/
cp work/source/code/VisitsServiceApplication.java work/build/spring-petclinic-visits-service/src/main/java/org/springframework/samples/petclinic/visits/
cp work/source/code/VetsServiceApplication.java work/build/spring-petclinic-vets-service/src/main/java/org/springframework/samples/petclinic/vets/
cp work/source/code/owner-details.controller.js work/build/spring-petclinic-static-service/src/main/resources/static/scripts/owner-details/

find work/build/spring-petclinic-static-service/src/main/java/org/springframework/samples/petclinic/api/ -mindepth 1 -maxdepth 1 -type d -exec rm -r "{}" \;
find work/build/spring-petclinic-static-service/src/test/java/org/springframework/samples/petclinic/api/ -mindepth 1 -maxdepth 1 -type d -exec rm -r "{}" \;

cd work/build && ./mvnw package 