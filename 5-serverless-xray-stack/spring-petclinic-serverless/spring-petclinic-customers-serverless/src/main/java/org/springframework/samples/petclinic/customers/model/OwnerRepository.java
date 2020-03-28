package org.springframework.samples.petclinic.customers.model;

import java.util.UUID;

import org.socialsignin.spring.data.dynamodb.repository.EnableScan;
import org.springframework.data.repository.CrudRepository;

@EnableScan()
public interface OwnerRepository extends CrudRepository<Owner, UUID> {

}
