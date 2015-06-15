select libertarians.*, national.*
from libertarians_national
  INNER JOIN libertarians
     on libertarians.SOS_VOTERID = libertarians_national.libertarian_id
  INNER JOIN national
     ON national.id = libertarians_national.national_id
