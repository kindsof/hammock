# hammock
A good place to REST.
Hammock provides a friendly approach to develop resources for a REST server.
currently supports falcon.

## General

Your REST server might have resources.

1. Make a resources package somewhere in your project (with __init__.py and so on).
2. Add your resources to that package (see below).
3. Add the resources to the falcon API (see below).
4. Use the auto-generated client.
4. Use the auto-generated service API.

## Creating a resource
A resource defined by its URL prefix.
A resource is a class with name of its module, capitalized, and inherits from the `hammock.Resource`. Resource class:
Lets create an helloworld resource, in resources/helloworld.py:
```python
import hammock

class Helloworld(hammock.Resource):
  @hammock.get()
  def say(self):
    return "hello world"
```

This class definition will add a resource in the URL `/helloworld`. The `hammock.get` decorator
defines the say method as a rest method for `GET /helloworld`.

## Adding resources package to falcon API
Simply use this code:
```python
import hammock
from somewhere.in.your.project import resources

hammock.Hammock('falcon', resources)
```

## REST methods
As explained above, adding a rest method is done by adding a method to the resource class with an
appropriate decorator.
You can use one decorators: `hammock.get`, `hammock.post`, `hammock.put`, `hammock.patch` or `hammock.delete`.
The developer may write a method that gets arguments, or keyword arguments, and returns
something, usually an object that can be converted to JSON format in the response body. The arguments
will be parsed automatically from the request URL query or JSON body (depending on the method used), and the return
value will be written to the response message.

### The decorators may get some arguments:
- path (default: ""): representing a path in the resource. This path may include variables,
surrounded by curly braces, same as you would have done in falcon.
- success_code (default: 200): the code that will be returned with the HTTP response,
in case that no error was raised.
- result_content_type (default "application/json"): the content type that will be in the header of the response.
- rule_name: see [Policy](#policy), below.

## Route argument types

You may add types for the route method's arguments.
The types are given in the docstring of the method and also influence the CLI.
To document an argument, add line/lines to the docstring:
```python
"""
:param [<optional-param-type>] <param-name>: <param-doc (multiline)>
"""
```
The you define an argument type, the argument will be converted to the proper type
before entering your method. If an error occurs during the conversion, an HTTP 400 (Bad Request)
will be raised. Special cases:

- If a type is `list`, and a single item will be given, the item will be converted to a list with one item.
- The value `None` won't be converted and it will be passed as is. In the case of type `list`, an empty list
  will be passed to the method.

### Special arguments
Naming the method's argument in a special way, might result in a different behaviour:
- `_headers`: the argument that will be passed to the method is the headers of the request.
- `_file`: This method expects "application/octet-stream" as content-type of the request, and the stream
will be delivered to the `_file` argument. Notice that this method must be "PUT" or "POST".
Other arguments will be passed through the URL query parameters.
- `_list`: when JSON body is a list (and not a dict) the body will go to this variable.

## URLs
The URL of your resource is created using the python packages and class name.
For example, if your Echo class is in `your.project.resources.tools.echo.Echo`,
and you add the package `your.project.resources` to the rest.Rest class, the resource URL will be:
`/tools/echo`, since its class name is Echo and it is in subpackage tools.

### Overriding URLs
- For packages: if you want the URL component of a package to differ from its name,
you can add to the package `__init__.py` file: `PATH = "some-other-name"`. This will replace the package
name with `some-other-name` in the URL.
- For classes: adding PATH class member
```python
class SomeResource(hammock.Resource):
  PATH = "some-other-name"
```

## Client Methods:

In case you want that one route method will be expand to different 
methods in the generated client. you can use the route `client_methods`
argument, and map a method name to kwargs that will be enforced as part
of the client's request.

You can see this [example](./tests/client_methods.py).

## Policy

Define routing policies using a policy JSON file.
A policy rule is according to [oslo.policy](http://docs.openstack.org/developer/oslo.policy).
To use the policy file, instantiate the Hammock instance with
the policy_file keyword argument.
A rule has a name and a Boolean expression that is evaluated
using the headers and target resource parameters.
- The rule name is combined of rule-group and rule-name
  - The rule group is by default the resource class name, lowercase,
    and can be overridden using the `POLICY_GROUP_NAME` class member. Setting this
    member to `False` will result in no policy enforcement on the class.
  - The rule name is the route method name, and can be overridden using the
    `rule_name` keyword argument in the route decorator.
  - The full name is `{rule-group}:{rule-name}`
- The headers are converted to a credentials dict,
  by default using the [Credentials](./hammock/types/credentials.py) class,
  but can be customized using credentials_class parameter.
- The request is converted to a dict using hammock engine, and passed to oslo.policy as
  the target field.
- Evaluating the expression:
  the expression is key:value tuple. The key might be:
  * `rule`: then the target is reference to another rule.
  * `role`: then the value is looked up in a list stored in a key 'roles' in the credentials dict.
  * project_id/user_id/domain_id: the credential's project_id/user_id/domain_id.
  * other: the key is searched in the credentials rules, and then the value is compared after
    evaluating the python expression: value % target
  * [reference](http://docs.openstack.org/developer/oslo.policy/api/oslo_policy.html#policy-rule-expressions).
  * Example:
    rule is 'credentials_entry:%(target_entry)s', then
    if credentials are {'credentials_entry': 'x'} and target is {'target_entry': 'x'},
    then the rule is evaluated to True.
- The expression might have and/or parentheses.

### Enforcement in the route method context

Not all policies can be enforced in the route method entry level.
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

## CLI

A CLI for a hammock auto-generated client can be initiated using The `hammock.cli.app.App` class.
You can inherit it in your project, to override the prompt, description, version or proprties.
You initiate it using a list of hammock client classes. Notice that it expects classes and not instances. All the clients are merged into a one CLI.

### Command names

The CLI is populated with commands and sub commands using the client Class.
A Resource class in the client will be converted into a command, containing all its routing methods, or resource nested classes as sub commands (recursively). The name of the resource and routing methods will be conveted into a command name (no caps, dashes, etc...) automatically, but you can override this name as follows:

For resources package, add `CLI_COMMAND_NAME` variable in the `__init__.py` file of the package, for a resource class: add a `CLI_COMMAND_NAME` attribute, for a route method, use the `cli_command_name` parameter when you define it. The effect will be as follows:

- `None` will have no effect and the command name will be converted from the package/class/method name.
- `False` will remove the package/class/method from the CLI (and all its nested dependencies).
- any other string will be used as the command name.

### Command arguments

- The arguments for a command are taken from the route method it represents.
- `args` are converted to positional arguments. `kwargs` are converted to optional arguments.
- Type and documentation strings are taken from the method doc string: if the doc string contains a line(s): `:param [<optional-param-type>] <param-name>: <param-help(multi-line)>`.
  * The type can be `str`, `bool`, `int` of `float` to specify type.
  * `list` will define a CLI argparser `nargs='*'`.
  * `bool[False]` or `bool[True]` will use the `action='store_true'` or `action='store_false'` respectively, and type bool.
- Return value of a method can be defined using the doc string line(s): `:return <return-type>: <return-help(multi-line)>`, The return value affects the command as follows:
  * `dict`: means the return value is an item, the CLI will print a table with dict keys and values. The CLI will add option `-f` that can change the output format (JSON, YAML, etc...).
  * `list`: means the return value is a list of items. The CLI will print a table of the values for each item, will add the `-f` flag that can define the format, `-c` to select specific columns and more. It is best practice to return a list of dicts, containing the same keys. If a list of other types is returned, the CLI will convert it to a list of dicts containing one key `value`.
  * other types will be printed to the stdout of the CLI.


- The documentation string for the command is taken from the route method doc string.

# API generation

In order to dump a hammock service API into a file:
`python -m hammock.doc path.to.resource_package [--json|--yaml] > my-resource-api.yml`

The API json can also be obtained from a running hammock service:
`curl http://your-server/_api`


## Examples:

* Look at the resources test [package](./tests/resources).
* Look at the example [project](./examples/phoenix)
