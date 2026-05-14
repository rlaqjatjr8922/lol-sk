# generated file


def calculate_reward(
    me,
    tagged_someone,
    got_tagged,
    dt,
):

    reward = 0.0

    # 술래
    if me.is_tagger:

        me.hp -= 10 * dt

        # 술래 상태 유지 약한 패널티
        reward -= 0.01

    # 도망자
    else:

        # 안 잡힌 상태 약한 보상
        reward += 0.01

    # 잡음
    if tagged_someone:
        reward += 100

    # 잡힘
    if got_tagged:
        reward -= 100

    return reward