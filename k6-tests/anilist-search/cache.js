import http from 'k6/http';
import { check } from 'k6';

const BASE_URL = 'http://localhost:8000';
const MEDIA_TYPE = 'anime';

export const options = {
  vus: 20,
  duration: '30s',
};

const popularQueries = [
  '?perPage=20&page=1&sort=POPULARITY_DESC',
  '?perPage=20&page=2&sort=POPULARITY_DESC',
  '?perPage=20&page=3&sort=POPULARITY_DESC',
  '?perPage=20&page=1&sort=TRENDING_DESC',
  '?perPage=20&page=2&sort=TRENDING_DESC',
  '?perPage=20&page=3&sort=TRENDING_DESC',

  '?perPage=20&page=1&sort=POPULARITY_DESC&season=SPRING&seasonYear=2026&status=RELEASING',
  '?perPage=20&page=2&sort=POPULARITY_DESC&season=SPRING&seasonYear=2026&status=RELEASING',
  '?perPage=20&page=3&sort=POPULARITY_DESC&season=SPRING&seasonYear=2026&status=RELEASING',

  '?perPage=20&page=1&sort=POPULARITY_DESC&season=SUMMER&seasonYear=2026&status=NOT_YET_RELEASED',
  '?perPage=20&page=2&sort=POPULARITY_DESC&season=SUMMER&seasonYear=2026&status=NOT_YET_RELEASED',
  '?perPage=20&page=3&sort=POPULARITY_DESC&season=SUMMER&seasonYear=2026&status=NOT_YET_RELEASED',

  '?sort=POPULARITY_DESC&genreIn=Comedy&genreIn=Adventure',
  '?sort=POPULARITY_DESC&genreIn=Fantasy&genreIn=Action'
];

function randomQuery() {
  const years = [2020, 2021, 2022, 2023, 2024, 2025];
  const genres = ['Action', 'Drama', 'Fantasy', 'Comedy', 'Romance', 'Horror'];
  const tags = ['school', 'Shounen', 'isekai', 'sports'];
  const seasons = ['WINTER', 'SPRING', 'SUMMER', 'FALL'];
  const countries = ['JP', 'KR', 'CN'];

  const year = years[Math.floor(Math.random() * years.length)];
  const genre1 = genres[Math.floor(Math.random() * genres.length)];
  let genre2 = genres[Math.floor(Math.random() * genres.length)];
  while (genre2 === genre1) {
    genre2 = genres[Math.floor(Math.random() * genres.length)];
  }
  const tag1 = tags[Math.floor(Math.random() * tags.length)];
  let tag2 = tags[Math.floor(Math.random() * tags.length)];
  while (tag2 === tag1) {
    tag2 = tags[Math.floor(Math.random() * tags.length)];
  }
  const season = seasons[Math.floor(Math.random() * seasons.length)];
  const page = Math.floor(Math.random() * 5) + 1;
  const country = countries[Math.floor(Math.random() * countries.length)];

  return `?page=${page}&perPage=20&sort=POPULARITY_DESC&season=${season}&seasonYear=${year}&genreIn=${genre1}&genreIn=${genre2}&tagIn=${tag1}&tagIn=${tag2}&countryOfOrigin=${country}`;
}

const rareQueries = [
  '?sort=POPULARITY_DESC&season=SUMMER&seasonYear=2023&genreIn=Drama&tagIn=Isekai&format=TV',
  '?sort=POPULARITY_DESC&genreIn=Comedy&tagIn=Cosmic+Horror&countryOfOrigin=JP&format=OVA'
];

export default function () {
  const rand = Math.random();

  let query;
  let type;

  if (rand < 0.7) {
    query = popularQueries[Math.floor(Math.random() * popularQueries.length)];
    type = 'popular';
  } else if (rand < 0.9) {
    query = randomQuery();
    type = 'random';
  } else {
    query = rareQueries[Math.floor(Math.random() * rareQueries.length)];
    type = 'rare';
  }

  const url = `${BASE_URL}/media/anilist/search/${MEDIA_TYPE}${query}`;

  const res = http.get(url, {
    tags: { scenario_type: type },
  });

  check(res, {
    'status is 200': (r) => r.status === 200,
  });
}