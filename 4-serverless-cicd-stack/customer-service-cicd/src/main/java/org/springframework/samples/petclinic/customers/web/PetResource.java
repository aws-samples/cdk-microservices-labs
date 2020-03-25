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
 
package org.springframework.samples.petclinic.customers.web;

import io.micrometer.core.annotation.Timed;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.samples.petclinic.customers.model.*;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;
import java.util.ArrayList;
import java.util.UUID;

/**
 * @author Juergen Hoeller
 * @author Ken Krebs
 * @author Arjen Poutsma
 * @author Maciej Szarlinski
 */
@RestController
@Timed("petclinic.pet")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
@Slf4j
class PetResource {

    private final OwnerRepository ownerRepository;


    @GetMapping("/petTypes")
    public List<String> getPetTypes() {
        List<String> petTypes = new ArrayList<>();
        petTypes.add("cat");
        petTypes.add("dog");
        petTypes.add("bird");
        petTypes.add("lizard");
        petTypes.add("snake");
        petTypes.add("hamster");
        return petTypes;
    }

    @PostMapping("/owners/{ownerId}/pets")
    @ResponseStatus(HttpStatus.CREATED)
    public Owner processCreationForm(
        @RequestBody PetRequest petRequest,
        @PathVariable("ownerId") String ownerId) {

        final Pet pet = new Pet();
        pet.setName(petRequest.getName());
        pet.setBirthDate(petRequest.getBirthDate());
        pet.setType(petRequest.getType());
        final Optional<Owner> optionalOwner = ownerRepository.findById(UUID.fromString(ownerId));
        Owner owner = optionalOwner.orElseThrow(() -> new ResourceNotFoundException("Owner "+ownerId+" not found"));
        owner.getPets().add(pet);

        return ownerRepository.save(owner);
    }

    @PutMapping("/owners/{ownerId}/pets/{name}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void processUpdateForm(
        @RequestBody PetRequest petRequest,
        @PathVariable("ownerId") String ownerId,
        @PathVariable("name") String name) {
        
        save(name, petRequest, UUID.fromString(ownerId));
    }
    

    private Owner save(final String name, final PetRequest petRequest, final UUID ownerId) {

        Optional<Owner> optionalOwner = ownerRepository.findById(ownerId);
        Owner owner = optionalOwner.orElseThrow(() -> new ResourceNotFoundException("Owner "+ownerId+" not found"));
        List<Pet> pets = owner.getPets();
        Pet p = pets.stream()
            .filter(pt -> pt.getName().equals(name))
            .findFirst()
            .get();
        pets.remove(p);
        Pet pet = new Pet(name, petRequest.getBirthDate(),petRequest.getType());
        
        pets.add(pet);
        owner.setPets(pets);

        log.info("Saving pet {}", pet);
        return ownerRepository.save(owner);
    }

    @GetMapping("owners/{ownerId}/pets/{name}")
    public PetDetails findPet(@PathVariable("ownerId") String ownerId, @PathVariable("name") String name) {
        Optional<Owner> optionalOwner = ownerRepository.findById(UUID.fromString(ownerId));
        Owner owner = optionalOwner.orElseThrow(() -> new ResourceNotFoundException("Owner "+ownerId+" not found"));
        return new PetDetails(findPetByOwnerAndName(ownerId, name), owner);
    }


    private Pet findPetByOwnerAndName(String ownerId, String petName) {
        Optional<Owner> optionalOwner = ownerRepository.findById(UUID.fromString(ownerId));
        Owner owner = optionalOwner.orElseThrow(() -> new ResourceNotFoundException("Owner "+ownerId+" not found"));
        
        Pet pet = owner.getPets().stream()
              .filter(p -> petName.equals(p.getName()))
              .findAny()
              .orElse(null);
              
        return pet;
    }

}
