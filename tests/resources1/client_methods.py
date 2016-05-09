from __future__ import absolute_import
import hammock
import hammock.types.func_spec as func_spec


ALLOWED_ACTIONS = {'run', 'jump'}


class ClientMethods(hammock.Resource):
    """
    This class is an example of how to write actions in REST resource.
    """

    POLICY_GROUP_NAME = False
    _specs = None

    @hammock.put(
        'action',
        client_methods={name: {'name': name} for name in ALLOWED_ACTIONS},
    )
    def action(self, name, **kwargs):
        if name not in ALLOWED_ACTIONS:
            raise hammock.exceptions.BadRequest('action {} not allowed'.format(name))
        self._check_specs(name, kwargs)
        return getattr(self, name)(**kwargs)

    def run(self, speed, distance=1):
        """
        Run!
        :param float speed: Running speed.
        :param float distance: Running distance
        :return float: Run duration.
        """
        return speed * distance

    def jump(self, times):
        """
        Jump!
        :param int times: Many times to jump
        :return int: Times.
        """
        return times

    @classmethod
    def _check_specs(cls, method_name, kwargs):
        if not cls._specs:
            cls._specs = {
                name: func_spec.FuncSpec(getattr(cls, name))
                for name in ALLOWED_ACTIONS
            }
        try:
            cls._specs[method_name].check_match(**kwargs)
        except TypeError as exc:
            raise hammock.exceptions.BadRequest('Bad arguments: {}'.format(exc))
