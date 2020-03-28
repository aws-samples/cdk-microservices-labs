import { ApolloClient, createNetworkInterface } from 'react-apollo';

// 	http://dev.apollodata.com/react/initialization.html#creating-client
export const createGraphQLClient = () => {
  const networkInterface = createNetworkInterface({
    uri: 'https://xxxxx.appsync-api.ap-northeast-1.amazonaws.com/graphql'
  });

  networkInterface.use([{
	  applyMiddleware(req, next) {
	    if (!req.options.headers) {
	      req.options.headers = {};  // Create the header object if needed.
	    }
	    // get the authentication token from local storage if it exists
	    
	    req.options.headers['x-api-key'] = 'da2-xxxxx'
	    next();
	  }
	}]);


  const client = new ApolloClient({
    networkInterface: networkInterface
  });

  return client;
};
