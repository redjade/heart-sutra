# 반야심경 번역 프로젝트

수지독송을 위한 새로운 한국어 《반야심경》 번역을 만드는 작업 공간이다. 익숙한 현장 한역의 독송 전통을 살리면서, 산스크리트 전승을 대조하여 압축된 구절의 뜻과 중요한 판본 차이를 분명히 밝히는 것을 목표로 한다.

> 현재 번역·교정 중인 초안이다. 독송과 학술적 검토를 함께 거치며 표현과 주석이 달라질 수 있다. 오류나 다른 판본에 관한 제안은 GitHub 이슈로 남길 수 있다.

## 바로 읽기

- [반야바라밀다심경 한글 번역·번역 주·한문과 현토 독음](translation/01-heart-sutra.md)
- [구절별 번역 근거와 판본 기록](SOURCES.md)
- [번역 및 표기 원칙](translation/STYLE.md)

## 문서 형식

본문은 다음 순서로 작성한다.

1. `한글 번역`: 소리 내어 읽기 자연스러운 현대 한국어 번역
2. `번역 주`: 핵심 용어, 생략·보완 관계, 판본 차이에 관한 설명
3. `한문과 현토 독음`: 한문 원문과 순한글 현토 독음을 문장 또는 의미 단위로 나란히 제시

본문 번역에는 원문에 없는 해설이나 수행 조언을 섞지 않는다. 이해와 수행을 위한 글은 번역 주 또는 별도의 글로 분리한다.

## 번역 및 대조 원칙

- 독송의 한문 기준본은 현장(玄奘) 역 《般若波羅蜜多心經》, 《大正新脩大藏經》 T08, No. 251로 삼는다.
- 산스크리트 《Prajñāpāramitāhṛdaya》는 현장역의 압축된 표현을 이해하고 문구의 의미를 확인하는 대조 자료로 사용한다.
- 현장역과 산스크리트의 짧은 판본·긴 판본은 구성과 문구가 완전히 같지 않다. 어느 한 판본에만 있는 내용을 본문에 억지로 합치지 않고, 중요한 차이는 번역 주에 밝힌다.
- 한문 독음에는 `般若`를 `반야`로 읽는 것처럼 한국 불교의 관용음을 우선한다.
- 이 저장소에는 산스크리트 전문을 복제하여 저장하지 않는다. 산스크리트는 아래 원전 링크에서 대조하고, 번역 판단에 필요한 최소한의 어구만 번역 주에서 인용한다.

번역을 다듬으며 내린 세부 판단은 [SOURCES.md](SOURCES.md)에 누적한다. 번역 구절별 한문과 산스크리트 대응어, 채택한 번역과 그 이유, 해석의 배경 자료, 관련 판본, 확인 날짜와 URL을 함께 남긴다. 본문을 고칠 때에는 결과만 바꾸지 않고 해당 기록도 갱신하여, 이후 작업에서 판단의 근거와 판본 차이를 다시 확인할 수 있게 한다.

## 원전 링크와 이용 조건

- [CBETA T0251 XML](https://github.com/cbeta-org/xml-p5/blob/master/T/T08/T08n0251.xml): 현장 한역의 기준본이다. XML 헤더에는 원문 헤더를 온전히 보존하여 배포하는 경우 비영리 용도로 이용할 수 있다고 명시되어 있다. 이 자료를 재사용할 때에는 CBETA 출처와 XML 헤더를 보존한다.
- [Wikisource 현장본](https://zh.wikisource.org/zh/%E8%88%AC%E8%8B%A5%E6%B3%A2%E7%BE%85%E8%9C%9C%E5%A4%9A%E5%BF%83%E7%B6%93_(%E7%8E%84%E5%A5%98%E8%AD%AF)): 사람이 읽고 문장을 대조하기 편한 한문본이다. 해당 경전 원문은 페이지에서 공개 도메인으로 표시되며, Wikisource의 편집·사이트 텍스트는 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.ko)과 사이트 이용 조건을 따른다.
- F. Max Müller·Bunyiu Nanjio 편, *The Ancient Palm-leaves Containing the Pragñâ-pâramitâ-hṛdaya-sûtra and the Ushnîsha-vigaya-dhâranî* (1884): 초기 산스크리트 교정본과 사본 자료를 확인할 수 있는 공개 도메인 고판본이다. [Open Library 스캔](https://openlibrary.org/works/OL310423W/The_ancient_palm-leaves_containing_the_Pragn%CC%83a%CC%82-pa%CC%82ramita%CC%82-_Hridaya-Su%CC%82tra_and_the_Ushni%CC%82sha-vigaya-)과 [Google Books 스캔](https://books.google.com/books/about/The_Ancient_Palm_leaves_Containing_the_P.html?id=uy8TT8M3N5AC)에서 확인한다.
- [GRETIL 《Prajñāpāramitāhṛdayasūtra》](https://gretil.sub.uni-goettingen.de/gretil/1_sanskr/4_rellit/buddh/prajnhsu.htm): 검색 가능한 로마자 산스크리트 대조 자료이다. 현재 GRETIL 변환본은 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.ko)으로 배포되므로, 출처 표시·비영리·동일조건변경허락 조건을 따라야 한다.
- [DSBC 산스크리트 짧은 판본](https://www.dsbcproject.org/canon-text/content/401/1829): 다른 전자 판독본과 문구를 교차 확인하는 연구 자료이다. 전문 재배포에는 제한이 있으므로 [DSBC 이용 정책](https://www.dsbcproject.org/public/pages/usage-policy)을 따르고, 이 저장소에는 전문을 수록하지 않는다.

링크된 전자자료의 표점과 교정 판단이 서로 다를 수 있으므로, 한 자료만을 자동 전재하지 않고 CBETA 한문과 둘 이상의 산스크리트 자료를 함께 확인한다.

## 빨리어 자료에 관하여

《반야심경》은 산스크리트계 대승 반야경전이며, 이에 해당하는 빨리어 원문이나 전승된 빨리어 완본은 없다. 따라서 빨리어 자료를 《반야심경》의 원문 또는 직접적인 판본이라고 표시하지 않는다. 오온, 무아, 감각 영역, 연기처럼 주제가 맞닿는 빨리어 경전은 향후 `평행 가르침`이라는 별도 참고 자료로 연결하되, 《반야심경》의 본문 및 판본 계통과 분명히 구별한다.

## 라이선스

이 프로젝트에서 새로 작성한 한국어 번역, 번역 주, 해설 및 연구 기록은 별도 표시가 없는 한 [CC BY-NC-SA 4.0](LICENSE.md)으로 제공한다. 현장 한역을 비롯한 고전 원문과 CBETA·GRETIL·DSBC 등 외부 자료에는 각 자료의 권리와 이용 조건이 별도로 적용된다. 이 저장소의 라이선스는 외부 자료의 권리를 변경하지 않는다.
