# hammock
A good place to REST.
Hammock provides a friendly approach to develop resources for a REST server.
currently supports falcon.

## General.

Your REST server might have resources.

1. Make a resources package somewhere in your project (with __init__.py and so).
2. Add your resources to that package (see below).
3. Add the resources to the falcon API (see below).
4. Use the auto-generated client.

## Creating a resource
A resource defined by its url prefix.
A resource is a class with name of its module, capitalized, and inherits from the resource.Resource class:
Lets create an helloworld resource, in resources/helloworld.py:
```python
import hammock

class Helloworld(hammock.Resource):
  @hammock.get()
  def say(self):
    return "hello world"
```

This class definition will add a resource in the url `/helloworld`. The `hammock.get` decorator
defines the say method as a rest method for `GET /helloworld`.

## Adding resources package to falcon api
Simply use this code:
```python
import hammock
from somewhere.inn.your.project import resources

hammock.Hammock('falcon', resources)
```

## rest methods.
As explained above, adding a rest method is done by adding a method to the resource class with an 
appropriate decorator.
You can use one decorators: `resource.get`, `resource.post`, `resource.put` and `resource.delete`.
The developer may write a method that gets arguments, or keyword arguments, and returns
something, usually an object that can be converted to json in the response body. The arguments
will be parsed automatically from the request url query or json body (depends on the method used), and the return
value will be written to the response message.

### The decorators may get some arguments:
- path (default: ""): representing a path in the resource. this path may include variables, 
surrounded by curly braces, same as you would have done in falcon.
- success_code (default: 200): the code that will be returned with the HTTP response, 
in case that no error was raised.
- result_content_type (default "application/json"): the content type that will be in the header of the response.

### Special arguments.
Naming the method's argument in a special way, might result in a different behaviour:
- `_headers`: the argument that will be passed to the method is the _headers of the request.
- `_file`: This method expects "application/octet-stream" as content-type of the request, and the stream 
will be delivered to the `_file` argument. Notice that this method must be "PUT" or "POST". 
Other arguments will be passed through the url query parameters.
- `_list`: when json body is a list (and not a dict) the body will go to this variable.

## url:
The url of your resource is created using the python packages and class name. 
For example, if your Echo class is in: `your.project.resources.tools.echo.Echo`, 
and you add the package `your.project.resources` to the rest.Rest class, the resource url will be: 
`/tools/echo`, since it's class name is Echo and it is in subpackage tools.

### overriding url
- For packages: if you want that the url component of a package to defer from it's name, 
you can add to the package `__init__.py` file: `PATH = "some-other-name". This will replace the package 
name with `some-other-name` in the url.
- For classes: adding PATH class member
```python
class SomeResource(hammock.Resource):
  PATH = "some-other-name"
```

## Policy

Define routing policies using a policy json file.
A policy rule is according to [oslo.policy](http://docs.openstack.org/developer/oslo.policy).
To use the policy file, instantiate the Hammock instance with
the policy_file keyword argument.
A rule has a name and a boolean expression that is evaluated
using the headers and target resource parameters.
- The rule name is combined of rule-group and rule-name, 
  - The rule group is by default the resource class name, lowercase, 
    and can be override using the `POLICY_GROUP_NAME` class member. setting this
    member to `False` will result in no policy enforcement on the class.
  - The rule name is the route method name, and can be override using the
    `rule_name` keyword argument in the route decorator.
  - The full name is `{rule-group}:{rule-name}`
- The headers are converted to a credentials dict, 
  by default using [Credentials](./hammock/types/credentials.py) class.
  but can be customized using credentials_class parameter.
- The request is converted to a dict using hammock engine, and passed to oslo.policy as
  the target field.
- Evaluating the expression:
  The expression is key:value tuple, The key might be:
  * rule: then the target is reference to another rule.
  * role: then the value is looked up in a list stored in a key 'roles' in the credentials dict.
  * project_id/user_id/domain_id: the credential's project_id/user_id/domain_id.
  * other: the key is searched in the credentials rules, and then the value is compared after
    evaluating the python expression: value % target
  * [reference](http://docs.openstack.org/developer/oslo.policy/api/oslo_policy.html#policy-rule-expressions).
  * Example:
    rule is 'credentials_entry:%(target_entry)s', then
    if credentials are {'credentials_entry': 'x'} and target is {'target_entry': 'x'},
    then the rule is evaluated to True.
- The expression might have and/or parentheses.

### Enforcement in the route method context.

Not all policy can be enforced in the route method entry level.
The credentials dict might be injected to the route method, using
the `_credentials` keyword argument. For example:

```python
import hammock
import manager

class MySecuredResource(hammock.Resource):
    @hammock.get()
    def get(self, _credentials, resource_id):
        resource = manager.get(resource_id)
        if resource['project_id'] != _credentials['project_id']:
            raise exceptions.Unauthorized('Get secured resource {}'.format(resource_id))
        return vm
```

## Examples:

* Look at the resources test [package](./tests/resources).
* Look at the example [project](./examples/phoenix)
