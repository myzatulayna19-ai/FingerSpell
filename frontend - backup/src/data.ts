// import ADemonstration from "./assets/A.jpg";
import { Lesson, DictionaryWord, Achievement } from './types';

export const INITIAL_LESSONS: Lesson[] = [
  {
    id: 'lesson_1_2',
    title: 'Abjad: "A"',
    category: 'Abjad',
    level: 'Beginner',
    instructorImage: "/A.jpg",
    instruction: 'Fold all four fingers into a fist while keeping the thumb straight.',
    description: 'Hold the position steadily until the system confirms your gesture.',
    progress: 75,
    xpReward: 10,
    tip: 'Keep all four fingers fully folded and your thumb close to the side of your hand.',
    signPhrase: ''
  },
  {
    id: 'lesson_1_3',
    title: 'Courtesy: "Terima Kasih"',
    category: 'Greetings',
    level: 'Beginner',
    instructorImage: 'https://lh3.googleusercontent.com/aida-public/AB6AXuD-y2tzoOMkGZpvO2mqXK7xlBrLm1jyoLiOBAhvrQZM59BfLRiTkKJ0VPkpY0ryGK2zGqKKIUKBy5DlVt4M7dO8UXvKAENYjee0pP2m8ka-_YOIivDttWNL00AOaUaGY5HoRAPZf77CWP8p8ca4IfYnRA8vMifTDcYc7Czk9VkWjQabp43YGpAzZ-9MZJM36M5ZaZJdcHHRRiWZ3CdNk3tcODQyw1Up4O3QYMjAoFOYAUBqD0SIMKJIbSdJ27K2YkeBTakyyfo7gXnH',
    instruction: 'Touch your fingers of your flat hand to your lips and move them forward.',
    description: 'Move your hand away from your chin towards the reader. Keep a friendly, appreciative facial expression (non-manual marker) to convey warmth.',
    progress: 0,
    xpReward: 10,
    tip: 'Your palm should face toward you at the start, then rotate forward.',
    signPhrase: 'Abjad A'
  }
];

export const INITIAL_WORDS: DictionaryWord[] = [
  {
    id: 'dict_assalamualaikum',
    phrase: 'Assalamualaikum',
    category: 'Greetings',
    level: 'Beginner',
    imageUrl: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAZehBuh27F6GOOavA0ANpxMDk7DXrBF9zfX8tHJXHwdKY3RESqfjNtPHwFMVUMp0DyCQMWgF6VVwEZ2_0ZUYHvIXhrkJYwbA7fGtQ66zjlMDRPYsBbPgoigm2r2YmxB4Srhnox-mNyGMmqg8GiR3koqfrUzMiZga9wzUP6GHFfoAjidB7_UG_vObzJxfYoZ_BOwHdoBK08tpLmG-PU6CM4YCsCsl_tcvJ-Ynt0GG2BTNZUIQsrrtFM4n8gQyof1Jg2DluQGRr2UbfH',
    summary: 'A respectful Islamic greeting commonly used in Bahasa Isyarat Malaysia (BIM).',
    description: 'The sign for "Assalamualaikum" begins with the "A" handshape. Form a fist with all four fingers folded while keeping the thumb straight beside the index finger. Raise the hand beside the forehead, then move it gently forward and outward in one smooth motion.',
    handShape: 'Letter "A" handshape – all four fingers folded into a fist with the thumb resting straight against the side of the index finger.',
    armMovement: 'Raise the hand beside the forehead, then move it forward and slightly outward in a smooth, natural motion.',
    facialExpression: 'Maintain a warm smile and friendly eye contact to convey a respectful greeting.',
    fingerSpelling: ['A'],
    culturalContext: '“Assalamualaikum” is a common Islamic greeting meaning “Peace be upon you.” In BIM, it is expressed with a respectful hand movement and is widely used when greeting others.',
    isBookmarked: true
  },
  {
    id: 'dict_thank_you',
    phrase: 'Thank You',
    category: 'Greetings',
    level: 'Beginner',
    imageUrl: 'https://lh3.googleusercontent.com/aida-public/AB6AXuD-y2tzoOMkGZpvO2mqXK7xlBrLm1jyoLiOBAhvrQZM59BfLRiTkKJ0VPkpY0ryGK2zGqKKIUKBy5DlVt4M7dO8UXvKAENYjee0pP2m8ka-_YOIivDttWNL00AOaUaGY5HoRAPZf77CWP8p8ca4IfYnRA8vMifTDcYc7Czk9VkWjQabp43YGpAzZ-9MZJM36M5ZaZJdcHHRRiWZ3CdNk3tcODQyw1Up4O3QYMjAoFOYAUBqD0SIMKJIbSdJ27K2YkeBTakyyfo7gXnH',
    summary: 'Touch the fingertips of your flat hand to your mouth and extend them forward.',
    description: 'Start with the fingers of your flat dominant hand near your chin or mouth. Arcar the hand outwards towards the person you are thanking, flat layout.',
    handShape: 'Open, flat hand-shape with fingers strictly pressed together.',
    armMovement: 'Swing hand down and out. Hand ends around rib level facing slightly up.',
    facialExpression: 'Grateful smile, gentle nod of the head.',
    fingerSpelling: ['T', 'H', 'A', 'N', 'K', 'Y', 'O', 'U'],
    culturalContext: 'Be cautious not to gesture too quickly as it might denote impatience or insincerity.',
    isBookmarked: false
  },
  {
    id: 'dict_apple',
    phrase: 'Apple',
    category: 'Food & Drink',
    level: 'Beginner',
    imageUrl: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCgNrd0kuGCuxg_ePa8UZqXprbS8ASrO9-3qr2LY1uMy83_2Ps_hGfx5vrOkeiqTxpV1fBGEQfVDPPZibKdGoHejWSrPxe4j29O1i5_zsVRE0cJ5Y2KhPZZXLasl5y4ttdv980EO-ucYNjxwxXltlm3K8Euj4jNnPjdPrpJH91BdI74j7zuSJRkP4tCMJ7-I4eCHVmesyG6Btad-HWTtFwoYpULGYo4fY3RYPdf7qEusT7ehiwckayuYXwihbl0niU9Y1Q2iCEJchFl',
    summary: 'Twist the knuckle of your index folder into your cheek.',
    description: 'Pivot your index knuckle back and forth on your cheek near the corner of your smile.',
    handShape: 'Closed index loop knuckle (X handshape variation).',
    armMovement: 'Bring knuckles to cheek, pivot forward and back twice.',
    facialExpression: 'Soft relaxation or smile interest.',
    fingerSpelling: ['A', 'P', 'P', 'L', 'E'],
    culturalContext: 'A very common mnemonic sign used when first learning the ASL alphabet.',
    isBookmarked: false
  },
  {
    id: 'dict_tomorrow',
    phrase: 'Tomorrow',
    category: 'Time & Calendar',
    level: 'Beginner',
    imageUrl: 'https://lh3.googleusercontent.com/aida-public/AB6AXuASgEGa22RQKQL4KkcPlLUkwvh3SVAdIHifFhMLxFj3Jhe348opcv4Ro64-m5wAxnxZlqZxp5Umeu3MSRRC-7TyJgKvU-C22u3oJgEJtMrsoqWDWoymEe4vHq-bRDdi8JzFa13HDTP4KEBr8WZx7V7Ba4CDWDNgpFlzzkjSrzx973djdHemcvOzuzwfLsNIExWC_ggTJS9ULP2R5LCn7tPc6LgraR6K5--igdBlWKaZP5X0lwFkayIGHFiGD3kS-n5J8zZQRKk9trNV',
    summary: 'Push the tip of your thumb forward from your chin line.',
    description: 'Make a fist with thumb extended (ASL letter A). Place thumb under the cheek/jaw line and push forward.',
    handShape: 'A hand-shape with thumb pointing up.',
    armMovement: 'Push thumb outwards, slicing through empty posture.',
    facialExpression: 'Focused, steady gaze.',
    fingerSpelling: ['T', 'O', 'M', 'O', 'R', 'R', 'O', 'W'],
    culturalContext: 'Flipping or moving sign movements forward indicates the future, whereas gesturing backwards behind you denotes past.',
    isBookmarked: false
  },
  {
    id: 'dict_mother',
    phrase: 'Mother',
    category: 'Family',
    level: 'Beginner',
    imageUrl: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBY2dL_RAU3LUmcKEVeL11qiWD3m10bUbWSFTnjYKdpU0yBb8iiNL1gfXuE_jGgu48zossxgi_I7OXyUquZXfA7iETMTAUmMV8XvCbetLj3FToMbAKxAwE98KxlP_G8Bo2PQ5Nw7o11cmg5pwEHfFAcfM_Mu_YvbfTnjIurAiFCfpYIvD4J70ds8LU75v1Jex7AWYCiIyCOegOMntAUqPggMz0-VrGyYvkPohE8Xgrxny90AfEmMUPXyoOjmOZuaHcLwFs6Ht1YJlQ0',
    summary: 'Tap the thumb of your open hand against your chin twice.',
    description: 'Spread your fingers wide. Place your thumb on your chin and tap gently twice.',
    handShape: 'Open 5 handshape.',
    armMovement: 'Gentle double tap with thumb touching chin center.',
    facialExpression: 'Warm, caring smile.',
    fingerSpelling: ['M', 'O', 'T', 'H', 'E', 'R'],
    culturalContext: 'In ASL, masculine relatives (father, grandfather) are signed on the forehead, while feminine relatives are signed on the lower face/chin.',
    isBookmarked: false
  },
  {
    id: 'dict_coffee',
    phrase: 'Coffee',
    category: 'Food & Drink',
    level: 'Beginner',
    imageUrl: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCkCj5D_nbpUdIdIpuVoffDk5zci9DxEOqVpguJJ0IXCwtsIeuWY32SlOQl8r7VViFXH-noWS-Svg2r5ikYn9_aDhoKOkd0h6_lYGRqzmiz_GW4XF9_YGiK6alXklcruMHg7VQ8ylH8JdmyeCtTN9hBGOCNpwY24FO4mbudjiEsa1GwW_d2n3rVfZHaT_qGVoe6e1qABeuMM4Wm4i-6PmPUApMMzSew-lEoicJbCQdzGGSDxkAVUbvmx0cXEivB2MnjQJIbEDAfKMM4',
    summary: 'Rotate one fist directly on top of another, copying a coffee grinder.',
    description: 'Keep both hands in closed fists. Place dominant fist on top of your passive fist and make short horizontal circular milling trajectories.',
    handShape: 'Double closed "S" fist handshapes.',
    armMovement: 'Top hand circles clockwise, duplicating machine grinding grids.',
    facialExpression: 'Casual or curious eyes.',
    fingerSpelling: ['C', 'O', 'F', 'F', 'E', 'E'],
    culturalContext: 'The visual mimics the antique coffee mill cranks.',
    isBookmarked: false
  },
  {
    id: 'dict_happy',
    phrase: 'Happy',
    category: 'Emotions',
    level: 'Beginner',
    imageUrl: 'https://lh3.googleusercontent.com/aida-public/AB6AXuB4frMsEPElNGqbbxwjnm7NfJRhADMyTypT_BY_zHME7S0Q4fVVR3bBkNI8yb2Dzz-S8dcx0I5-R29XPXYEfFY9lXzxkLRvmZOxJ_GwDz8WcpS4dDGQgdBJpU6hj0FOE7skjufsXcEoqSL_DhUvoh1XQYZzOs8j97oKyZNIhNlYK4geyxwBGNHvwZMy5_VoZNluPjldM6cNaFwZIZQ0lRwSdzkbhLGjtplE1874_DSef10bi1dlSImRkheokldO0qkCAxn6EDK2R9Sc',
    summary: 'Brush flat hands upward against your chest synchronously twice.',
    description: 'Use flat open hands, palms facing inwards toward your chest. Sweep them up in small circles without touching your chest too heavily.',
    handShape: 'Flat, open 5-finger alignment.',
    armMovement: 'Upward circular loops matching buoyant positive vibes.',
    facialExpression: 'Wide enthusiastic expression, smiling warm eyes.',
    fingerSpelling: ['H', 'A', 'P', 'P', 'Y'],
    culturalContext: 'Your facial expression must explicitly match the emotive sign. Signing "happy" with a deadpan face represents grammatical conflict!',
    isBookmarked: false
  },
  {
    id: 'dict_house',
    phrase: 'House',
    category: 'Objects',
    level: 'Beginner',
    imageUrl: 'https://lh3.googleusercontent.com/aida-public/AB6AXuC6leWlzKGzhKOJzkG41N6XFCrevZYHd1x1Nt-pZo7b88GnEeaiBnylkh0j3CztvjRzVXmPvxMAUMmrV1doDqNXirDYb6-aJZVrgCty6cs4mxHEQMk6kRTegWVtuwNYGG6XjTZM3sQOmcNGefmHFMQZzq0DXM4JBOONM62COqsrLptpDR8VFoGlhyTxGb_Mu6BdCYtKjVU28O51iuSPhLrKBc1vWDRJum-7if1eKvm1Rmz7kpiMQVrW8rl1-nWiPPA_IdlEtaUbIEc9',
    summary: 'Trace the triangular roof and parallel walls of a house with flat fingers.',
    description: 'Touch fingers of flat hands together to form a pitched roof shape. Separate hands outwards to form parallel walls down.',
    handShape: 'Flat open hands touching fingers.',
    armMovement: 'Trace outlines of a building.',
    facialExpression: 'Relaxed neutral posture.',
    fingerSpelling: ['H', 'O', 'U', 'S', 'E'],
    culturalContext: 'A literal iconic sign showing a shape projection of an object.',
    isBookmarked: false
  }
];

export const INITIAL_ACHIEVEMENTS: Achievement[] = [
  {
    id: 'first_sign',
    title: 'First Sign',
    description: 'Fingerspelled and verified your very first correct sign gesture!',
    icon: 'Sparkles',
    color: 'from-blue-500 to-indigo-500',
    unlocked: true,
    unlockedAt: '2026-06-03'
  },
  {
    id: 'streak_7',
    title: '7-Day Warrior',
    description: 'Maintained a constant daily sign streak for one active week.',
    icon: 'Flame',
    color: 'from-orange-500 to-red-500',
    unlocked: true,
    unlockedAt: '2026-06-02'
  },
  {
    id: 'perfect_50',
    title: 'Form Expert',
    description: 'Achieved 50 perfect gesture alignment scores under raw camera tests.',
    icon: 'CheckCircle',
    color: 'from-emerald-500 to-teal-500',
    unlocked: false
  },
  {
    id: 'quick_learner',
    title: 'Quick Learner',
    description: 'Explored 10 completely fresh vocabulary signs in a single active session.',
    icon: 'Award',
    color: 'from-pink-500 to-rose-500',
    unlocked: false
  }
];
