'use strict';

angular.module('petForm')
    .controller('PetFormController', ['$http', '$state', '$stateParams', function ($http, $state, $stateParams) {
        var self = this;
        var ownerId = $stateParams.ownerId || 0;

        var createFlag = $stateParams.petName? false: true;

        $http.get(_baseUrl + 'api/customer/petTypes').then(function (resp) {
            self.types = resp.data;
        }).then(function () {

            var petName = $stateParams.petName || null;

            if (petName) { // edit
                $http.get(_baseUrl + "api/customer/owners/" + ownerId + "/pets/" + petName).then(function (resp) {
                    self.pet = resp.data;
                    self.pet.birthDate = new Date(self.pet.birthDate);
                    self.type = "" + self.pet.type;
                });
            } else {
                $http.get(_baseUrl +'api/customer/owners/' + ownerId).then(function (resp) {
                    self.pet = {
                        owner: resp.data.firstName + " " + resp.data.lastName
                    };
                    self.type = "cat";
                })

            }
        });

        self.submit = function () {

            var data = {
                name: self.pet.name,
                birthDate: self.pet.birthDate,
                type: self.type
            };

            var req;
            if (!createFlag) {
                req = $http.put(_baseUrl + "api/customer/owners/" + ownerId + "/pets/" + self.pet.name, data);
            } else {
                req = $http.post(_baseUrl + "api/customer/owners/" + ownerId + "/pets", data);
            }

            req.then(function () {
                $state.go("owners", {ownerId: ownerId});
            }, function (response) {
                var error = response.data;
                error.errors = error.errors || [];
                alert(error.error + "\r\n" + error.errors.map(function (e) {
                        return e.field + ": " + e.defaultMessage;
                    }).join("\r\n"));
            });
        };
    }]);
